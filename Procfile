# Production WSGI configuration
web: gunicorn main:app -w 1 -k uvicorn.workers.UvicornWorker --host 0.0.0.0 --port $PORT --preload
