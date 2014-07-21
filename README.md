qubell_portal_sample
====================

Demonstrates example of gui test.

Run

```bash
pip install -r requirements.txt

export QUBELL_TENANT=https://express.qubell.com
echo 'use basic auth user'
export QUBELL_USER=???
export QUBELL_PASSWORD=???

export wd_selenium_type=LOCAL
export wd_selenium_active=True

nosetests -d stories

```
