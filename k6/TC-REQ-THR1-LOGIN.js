import http from 'k6/http';
import { sleep } from 'k6';
import { check } from 'k6';

export let options = {
  vus: 10,
  duration: '10s',
};

export default function () {
  const url = 'http://172.26.80.1:5000/login';
  const payload = JSON.stringify({ username: 'hieult', password: 'nec@123' });
  const params = { headers: { 'Content-Type': 'application/json' } };

  let res = http.post(url, payload, params);
  check(res, {
    'is status 200': (r) => r.status === 200,
  });
  sleep(1);
}