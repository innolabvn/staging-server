import http from 'k6/http';
import { sleep } from 'k6';
import { check } from 'k6';

export let options = {
  vus: 5,
  duration: '10s',
};

export default function () {
  // 🟢 Step 1: Login
  const loginUrl = 'http://172.26.80.1:5000/login';
  const loginPayload = JSON.stringify({
    username: 'hieult',
    password: 'nec@123',
  });
  const loginParams = {
    headers: {
      'Content-Type': 'application/json',
    },
  };

  let loginRes = http.post(loginUrl, loginPayload, loginParams);
  check(loginRes, {
    'login status is 200': (r) => r.status === 200,
  });

  // 🟢 Step 2: Create Asset
  const assetUrl = 'http://172.26.80.1:5000/assets';
  const assetPayload = JSON.stringify({
    assetName: 'Printer A',
    category: 'Hardware',
    purchaseDate: '2024-06-01',
    value: 250,
    assignedTo: 'hieult',
    description: 'Printer in HQ room',
  });
  const assetParams = {
    headers: {
      'Content-Type': 'application/json',
    },
  };

  let assetRes = http.post(assetUrl, assetPayload, assetParams);
  check(assetRes, {
    'asset creation status is 200': (r) => r.status === 200,
  });

  sleep(1);
}
