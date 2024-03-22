import os
import random
import secrets

from subprocess import Popen
from requests.auth import HTTPBasicAuth
from locust import HttpUser, task, between
from locust import events

USER_COUNT = 2
RND_PASSWD = secrets.token_hex(16)
CONTAINER_NAME = "nc1"

"""
  Run before a test starts.

  Asynchronously generate the given number of users on a container running a Nextcloud instance. Number of generated users is kept low
  as the generation process is quite lengthy.

  All users share the same complex and pseudo-randomly generated password.
"""
@events.test_start.add_listener
def on_test_start(environment, **kwargs):
  processes = []
  for i in range(USER_COUNT):
    process = Popen(f"docker exec -e OC_PASS={RND_PASSWD} --user www-data {CONTAINER_NAME} /var/www/html/occ user:add user{i} --password-from-env", shell=True)
    processes.append(process)
  for process in processes:
    process.wait()

"""
  Run after a test ends.

  Asynchronously remove the users utilized during tests. Removing a user also removes the uploaded files. This ensures a "clean slate" for
  running subsequent tests.
"""
@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
  processes = []
  for i in range(USER_COUNT):
    process = Popen(f"docker exec --user www-data {CONTAINER_NAME} /var/www/html/occ user:delete user{i}", shell=True)
    processes.append(process)
  for process in processes:
    process.wait()

class NextcloudUser(HttpUser):
  wait_time = between(2, 5)

  """
    At the start of each test.

    Randomly pick one of the previously generated users and generate an authentication payload for it. This will be used
    in subsequent tests.
  """
  def on_start(self):
    user_idx = random.randrange(0, USER_COUNT)
    self.user_name = f'user{user_idx}'
    self.auth = HTTPBasicAuth(self.user_name, RND_PASSWD)

  """
    All following methods: actual tests.

    Open a previously generated file containing a fixed amount of *random* data:
      - very small (4 bytes)
      - small (1kb)
      - medium (1mb)
      - big (1gb)
    and upload such file to the specified endpoint, i.e. a Nextcloud WebDAV endpoint that accepts a PUT request for uploading files.

    Each task is repeated the specified number of times for good measure. Files are then discarded as described above.
  """
  @task(5)
  def upload_file_text(self):
    with open("locust/test.txt", "rb") as file:
      self.client.put(f"/remote.php/dav/files/{self.user_name}/txt_{secrets.token_hex(16)}", data=file, auth=self.auth)
      
  @task(5)
  def upload_file_1gb(self):
    remote_path = f"/remote.php/dav/files/{self.user_name}/1gb_{secrets.token_hex(16)}"
    with open("locust/1gb.data", "rb") as file:
      self.client.put(remote_path, data=file, auth=self.auth)

  @task(5)
  def upload_file_1kb(self):
    remote_path = f"/remote.php/dav/files/{self.user_name}/1kb_{secrets.token_hex(16)}"
    with open("locust/1kb.data", "rb") as file:
      self.client.put(remote_path, data=file, auth=self.auth)

  @task(5)
  def upload_file_1mb(self):
    remote_path = f"/remote.php/dav/files/{self.user_name}/1mb_{secrets.token_hex(16)}"
    with open("locust/1mb.data", "rb") as file:
      self.client.put(remote_path, data=file, auth=self.auth)