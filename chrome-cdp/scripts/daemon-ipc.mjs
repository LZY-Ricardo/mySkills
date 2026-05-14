import { existsSync, readFileSync, readdirSync, renameSync, unlinkSync, writeFileSync } from 'node:fs';
import net from 'node:net';
import { join } from 'node:path';

const PORT_PREFIX = 'cdp-';
const PORT_SUFFIX = '.port';

export function portFilePath(targetId, runtimeDir) {
  return join(runtimeDir, `${PORT_PREFIX}${targetId}${PORT_SUFFIX}`);
}

export function writePortFileAtomically(filePath, data) {
  const tempPath = `${filePath}.tmp.${process.pid}`;
  writeFileSync(tempPath, JSON.stringify(data), { mode: 0o600 });
  renameSync(tempPath, filePath);
}

export function readPortFile(filePath) {
  if (!existsSync(filePath)) return null;
  try {
    return JSON.parse(readFileSync(filePath, 'utf8'));
  } catch {
    return null;
  }
}

function isProcessAlive(pid) {
  try {
    process.kill(pid, 0);
    return true;
  } catch (error) {
    return error?.code === 'EPERM';
  }
}

export function listDaemonPortFiles(runtimeDir) {
  return readdirSync(runtimeDir)
    .filter((name) => name.startsWith(PORT_PREFIX) && name.endsWith(PORT_SUFFIX))
    .map((name) => {
      const targetId = name.slice(PORT_PREFIX.length, -PORT_SUFFIX.length);
      const filePath = join(runtimeDir, name);
      const data = readPortFile(filePath);
      if (!data?.pid || !data?.port || !data?.token) {
        try { unlinkSync(filePath); } catch {}
        return null;
      }
      if (!isProcessAlive(data.pid)) {
        try { unlinkSync(filePath); } catch {}
        return null;
      }
      return { targetId, filePath, ...data };
    })
    .filter(Boolean);
}

export function connectToDaemon(daemonInfo) {
  return new Promise((resolve, reject) => {
    const conn = net.connect({ host: '127.0.0.1', port: daemonInfo.port });
    conn.on('connect', () => {
      conn.write(JSON.stringify({ token: daemonInfo.token }) + '\n');
      resolve(conn);
    });
    conn.on('error', reject);
  });
}
