FROM python:3
ADD radbbot.py /
RUN pip install requests
RUN pip install slackclient
ENV SLACK_BOT_TOKEN=add bot app token here
CMD ["python", "./radbbot.py"]