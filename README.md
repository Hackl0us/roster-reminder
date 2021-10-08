# roster-reminder
A reminder for stand-up roster

## Run the project

### Setup database
The project use SQLite as database.
You can create tables refer to `roster.sql`.

The SQLite database file should be named to `roster.db` and place it under `db/` folder.

### Run with python
You have to modify the `SLACK_WEBHOOK_URL` variable if you would like to run the project.
```shell
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the project
python roster-reminder.py
```

### Run in Docker
You have to specify the following environment variables if you would like to run the project in Docker:
* `TZ`: Timezone. It will affect the judgement on holidays
* `SLACK_WEBHOOK_URL`: Slack Webhook URL. It can post the message to the corresponding channel / conversation.

```shell
docker run -d --name "roster-reminder" \
-e TZ="Asia/Shanghai" \
-e SLACK_WEBHOOK_URL="https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX" \
-p 5000:5000 \
-v /path/to/roster/db:/app/db \
--restart always \
hackl0us/roster-reminder:latest
```
