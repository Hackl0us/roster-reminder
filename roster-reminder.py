#!/usr/bin/env python3

import flask
import json
import os
import sqlite3
from datetime import datetime
from urllib import request

slack_webhook_url = os.environ['SLACK_WEBHOOK_URL']
holiday_api_url = 'http://timor.tech/api/holiday/info/'

app = flask.Flask(__name__)
app.config["DEBUG"] = False


def today_roster():
    roster = dict()
    db = sqlite3.connect('db/roster.db')
    c = db.cursor()

    # Check number of stash_roster
    num_of_stash_roster = c.execute("SELECT COUNT(*) FROM stand_up_roster_stash").fetchone()[0]
    num_of_today_mute_stash_roster = \
    c.execute("SELECT COUNT(*) FROM stand_up_roster_stash WHERE mute_for_today = 1").fetchone()[0]

    # CASE 1: Stash table is not empty & Someone is available
    if (num_of_stash_roster > 0) and (num_of_stash_roster > num_of_today_mute_stash_roster):
        print("CASE 1: Stash table is not empty & Someone is available")
        result = c.execute("SELECT * FROM stand_up_roster_stash WHERE mute_for_today = 0 ORDER BY id ASC LIMIT 1")

        for row in result:
            roster['id'] = row[0]
            roster['name'] = row[1]
            roster['slack_member_id'] = row[2]
            roster['type'] = "STASH"
    else:
        # CASE 2: Stash table is empty || None of stash rosters are available
        print("CASE 2: Stash table is empty OR None of stash rosters are available")
        result = c.execute("SELECT * from stand_up_roster WHERE is_today = 1")

        for row in result:
            roster['id'] = row[0]
            roster['name'] = row[1]
            roster['slack_member_id'] = row[2]
            roster['type'] = "NORMAL"

    db.close()
    print("today roster: roster_id:" + str(roster['id']) + ", name: " + roster['name'] + ", slack: " + roster[
        'slack_member_id'] + ", type: " + roster['type'])
    return roster


def move_to_next_roster(is_stash=False):
    db = sqlite3.connect('db/roster.db')
    c = db.cursor()

    # Get the last roster id
    last_roster_id = c.execute("SELECT id FROM stand_up_roster ORDER BY id DESC LIMIT 1").fetchone()[0]
    roster = today_roster()

    if (is_stash):
        if (roster['type'] == "STASH"):
            print("BRANCH 1")
            c.execute("UPDATE stand_up_roster_stash SET mute_for_today = 1 WHERE id = ?", (roster['id'],))
            db.commit()

        if (roster['type'] == "NORMAL"):
            print("BRANCH 2")
            c.execute("INSERT INTO stand_up_roster_stash (name, slack_member_id, mute_for_today) VALUES (?, ?, 1)",
                      (roster['name'], roster['slack_member_id']))
            db.commit()
            move_flag_to_next_roster(roster['id'])
    else:
        if (roster['type'] == "STASH"):
            print("BRANCH 3")
            c.execute("DELETE FROM stand_up_roster_stash WHERE id = ?", (roster['id'],))
            db.commit()

        if (roster['type'] == "NORMAL"):
            print("BRANCH 4")
            move_flag_to_next_roster(roster['id'])

    db.close()


def move_flag_to_next_roster(slack_member_id):
    db = sqlite3.connect('db/roster.db')
    c = db.cursor()

    last_roster_id = c.execute("SELECT id FROM stand_up_roster ORDER BY id DESC LIMIT 1").fetchone()[0]

    if (slack_member_id == last_roster_id):
        c.execute(
            "UPDATE stand_up_roster SET is_today = 1 WHERE id = (SELECT id FROM stand_up_roster ORDER BY id ASC LIMIT 1)")
        db.commit()
    else:
        c.execute(
            "UPDATE stand_up_roster SET is_today = 1 WHERE id = (SELECT id FROM stand_up_roster WHERE id > ? ORDER BY id LIMIT 1)",
            (slack_member_id,))
        db.commit()

    c.execute("UPDATE stand_up_roster SET is_today = 0 WHERE id = ?", (slack_member_id,))
    db.commit()


def send_alert(slack_member_id):
    raw_payload = {"text": "Today\'s Stand-up Roster is <@" + slack_member_id + ">"}
    data = json.dumps(raw_payload)
    data = bytes(data, 'utf8')

    req = request.Request(slack_webhook_url, data=data, method='POST')
    req.add_header('Content-Type', 'text/json; charset=utf-8')
    request.urlopen(req).read()


def remove_roster(slack_member_id):
    db = sqlite3.connect('db/roster.db')
    c = db.cursor()
    c.execute("DELETE FROM stand_up_roster WHERE slack_member_id = ?", (slack_member_id,))
    c.execute("DELETE FROM stand_up_roster_stash WHERE slack_member_id = ?", (slack_member_id,))
    db.commit()
    db.close()


def task_daily_cleanup():
    db = sqlite3.connect('db/roster.db')
    c = db.cursor()
    c.execute("UPDATE stand_up_roster_stash SET mute_for_today = 0")
    db.commit()
    db.close()


def task_truncate_stash_table():
    db = sqlite3.connect('db/roster.db')
    c = db.cursor()
    c.execute("DELETE FROM stand_up_roster_stash")
    c.execute("DELETE FROM sqlite_sequence WHERE name='stand_up_roster_stash'")
    db.commit()
    db.close()


def is_holiday():
    format_current_date = datetime.today().strftime('%Y-%m-%d')
    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36 Edg/94.0.992.31'

    req = request.Request(holiday_api_url + format_current_date)
    req.add_header('Content-Type', 'application/json')
    req.add_header('User-Agent', user_agent)
    resp = request.urlopen(req).read()

    today_type = json.loads(resp)['type']['type']

    if (today_type == 1) | (today_type == 2):
        return True
    else:
        return False


# Slack slash command forces to use POST method
@app.route('/roster/today', methods=['POST'])
def api_get_roster():
    if not is_holiday():
        roster = today_roster()
        send_alert(roster['slack_member_id'])
        return roster
    else:
        return "Enjoy your holiday!"


# Slack slash command forces to use POST method
@app.route('/roster/skip', methods=['POST'])
def api_stash_roster():
    move_to_next_roster(is_stash=True)
    roster = today_roster()
    send_alert(roster['slack_member_id'])
    return roster


@app.route('/roster/remove', methods=['DELETE'])
def api_remove_roster():
    remove_roster(today_roster()['slack_member_id'])
    return "Done"


@app.route('/task/daily', methods=['PATCH'])
def api_task_daily_cleanup():
    if not is_holiday():
        move_to_next_roster(is_stash=False)
        task_daily_cleanup()
        return today_roster()
    else:
        return "Today is not workday, I'll do nothing!"


@app.route('/task/stash-truncate', methods=['DELETE'])
def api_task_truncate_stash_table():
    task_truncate_stash_table()
    return "Done"


if __name__ == "__main__":
    app.run()
