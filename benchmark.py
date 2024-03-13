import os
import random
from locust import HttpUser, task, between
from requests.auth import HTTPBasicAuth

class NextcloudUser(HttpUser):
  auth = None
  user_name = "aaaa"
  wait_time = between(2, 5)

  def on_start(self):
    user_idx = random.randrange(0, 30)
    # self.user_name = f'locust_user{user_idx}'
    self.auth = HTTPBasicAuth(self.user_name, 'QbrsVmyH9S9!j@av')

  @task(5)
  def propfind(self):
    self.client.request("PROPFIND", f"/remote.php/dav/files/{self.user_name}/", auth=self.auth)

  # @task(5)
  # def read_file(self):
  #   self.client.get(f"/remote.php/dav/files/{self.user_name}/Readme.md", auth=self.auth)

  @task(10)
  def upload_file_text(self):
    with open("locust/test.txt", "rb") as file:
      self.client.put(f"/remote.php/dav/files/{self.user_name}/test.txt", data=file, auth=self.auth)
      
  @task(1)
  def upload_file_1gb(self):
    remote_path = f"/remote.php/dav/files/{self.user_name}/1gb_file_{random.randrange(0, 10)}"
    with open("locust/1gb.data", "rb") as file:
      self.client.put(remote_path, data=file, auth=self.auth)

  @task(10)
  def upload_file_1kb(self):
    remote_path = f"/remote.php/dav/files/{self.user_name}/1kb_file_{random.randrange(0, 10)}"
    with open("locust/1kb.data", "rb") as file:
      self.client.put(remote_path, data=file, auth=self.auth)

  @task(5)
  def upload_file_1mb(self):
    remote_path = f"/remote.php/dav/files/{self.user_name}/1mb_file_{random.randrange(0, 10)}"
    with open("locust/1mb.data", "rb") as file:
      self.client.put(remote_path, data=file, auth=self.auth)