import assert from 'node:assert/strict';
import { mkdtempSync, existsSync, mkdirSync } from 'node:fs';
import net from 'node:net';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

import {
  connectToDaemon,
  listDaemonPortFiles,
  portFilePath,
  readPortFile,
  writePortFileAtomically,
} from './daemon-ipc.mjs';

async function testWriteAndReadPortFile() {
  const baseDir = mkdtempSync(join(tmpdir(), 'cdp-ipc-test-'));
  const filePath = portFilePath('ABC123', baseDir);
  const data = { port: 31337, pid: process.pid, token: 'secret-token', ts: Date.now() };

  writePortFileAtomically(filePath, data);

  assert.deepEqual(readPortFile(filePath), data);
}

async function testListDaemonPortFilesFiltersStaleEntries() {
  const baseDir = mkdtempSync(join(tmpdir(), 'cdp-ipc-test-'));
  const liveDir = join(baseDir, 'live');
  mkdirSync(liveDir, { recursive: true });

  writePortFileAtomically(portFilePath('LIVE1234', liveDir), {
    port: 31338,
    pid: process.pid,
    token: 'live-token',
    ts: Date.now(),
  });
  const stalePath = portFilePath('DEAD1234', liveDir);
  writePortFileAtomically(stalePath, {
    port: 31339,
    pid: 999999,
    token: 'dead-token',
    ts: Date.now(),
  });

  const daemons = listDaemonPortFiles(liveDir);

  assert.equal(daemons.length, 1);
  assert.equal(daemons[0].targetId, 'LIVE1234');
  assert.equal(existsSync(stalePath), false);
}

async function testConnectToDaemonSendsAuthLine() {
  let authLine = null;
  const server = net.createServer((conn) => {
    let buffer = '';
    conn.on('data', (chunk) => {
      buffer += chunk.toString();
      const newlineIndex = buffer.indexOf('\n');
      if (newlineIndex === -1) return;
      authLine = JSON.parse(buffer.slice(0, newlineIndex));
      conn.end();
    });
  });

  await new Promise((resolve) => server.listen(0, '127.0.0.1', resolve));

  try {
    const { port } = server.address();
    const conn = await connectToDaemon({ port, token: 'auth-token' });

    await new Promise((resolve) => conn.on('close', resolve));
    assert.deepEqual(authLine, { token: 'auth-token' });
  } finally {
    server.close();
    await new Promise((resolve) => server.on('close', resolve));
  }
}

const tests = [
  ['writePortFileAtomically writes data readable by readPortFile', testWriteAndReadPortFile],
  ['listDaemonPortFiles filters out stale daemon files', testListDaemonPortFilesFiltersStaleEntries],
  ['connectToDaemon authenticates using the token as the first line', testConnectToDaemonSendsAuthLine],
];

let failed = false;

for (const [name, fn] of tests) {
  try {
    await fn();
    console.log(`PASS ${name}`);
  } catch (error) {
    failed = true;
    console.error(`FAIL ${name}`);
    console.error(error.stack || error.message);
  }
}

if (failed) {
  process.exit(1);
}
