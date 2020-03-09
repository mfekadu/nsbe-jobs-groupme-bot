heroku container:login

heroku container:push -a nsbe-jobs-groupme-bot web

heroku container:release -a nsbe-jobs-groupme-bot web
