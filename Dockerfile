#FROM python: 3-onbuild
#COPY . / app
#CMD ["python","app.py"]

# docker build -t my_docker_flask:latest .
# docker run -p 5000:5000 my_docker_flask:latest 

# docker ps (shows ids)
# docker kill (container id)

#running on http://127.0.0.1:5000/ not http://0.0.0.0:5000/ 



FROM python:3.8
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
ENTRYPOINT ["python"]
CMD ["app.py"]