# roster-reminder
A reminder for stand-up roster

## Run the project

### Run with python
You have to modify the `SLACK_WEBHOOK_URL` variable if you would like to run the project.
```shell
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the project
python roster-reminder.py
```

### Run in Docker
You have to specify the `SLACK_WEBHOOK_URL` if you would like to run the project in Docker.
```shell
docker run -d --name "roster-reminder" \
-e SLACK_WEBHOOK_URL="https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX" \
-p 5000:5000 \
-v /path/to/roster/db:/app/db \
--restart always \
hackl0us/roster-reminder:latest
```
