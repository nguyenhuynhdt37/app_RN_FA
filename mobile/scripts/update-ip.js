const fs = require('fs');
const os = require('os');
const path = require('path');

function getLocalIp() {
  const interfaces = os.networkInterfaces();
  for (const name of Object.keys(interfaces)) {
    for (const iface of interfaces[name]) {
      // Skip internal and non-IPv4 addresses
      if (iface.family === 'IPv4' && !iface.internal) {
        return iface.address;
      }
    }
  }
  return 'localhost';
}

const envPath = path.join(__dirname, '../.env');
const localIp = getLocalIp();

if (fs.existsSync(envPath)) {
  let content = fs.readFileSync(envPath, 'utf8');
  
  // Robust regex to find EXPO_PUBLIC_API_URL=http://<IP>:<PORT>/<PATH>
  // Captures: prefix (EXPO_PUBLIC_API_URL=http://), current ip ([0-9.]+), and suffix (rest of line)
  const regex = /^(EXPO_PUBLIC_API_URL=http:\/\/)([0-9.]+)(:\d+.*)$/m;
  
  const updatedContent = content.replace(regex, (match, prefix, oldIp, suffix) => {
    return `${prefix}${localIp}${suffix}`;
  });

  if (content !== updatedContent) {
    fs.writeFileSync(envPath, updatedContent);
    console.log(`✅ Updated mobile/.env: EXPO_PUBLIC_API_URL to ${localIp}`);
  } else {
    console.log(`ℹ️ mobile/.env is already up to date (${localIp})`);
  }
}

// Update backend .env
const backendEnvPath = path.join(__dirname, '../../backend/.env');
if (fs.existsSync(backendEnvPath)) {
  let content = fs.readFileSync(backendEnvPath, 'utf8');
  
  // Update BACKEND_URL
  let updatedContent = content.replace(
    /^(BACKEND_URL=http:\/\/)([0-9.]+)(:\d+.*)$/m,
    (match, prefix, oldIp, suffix) => `${prefix}${localIp}${suffix}`
  );

  // Update CORS_ORIGINS (it's a JSON array)
  // We want to replace the old IP entries with the new IP
  // This is a bit trickier, let's just find the IPs and replace them
  updatedContent = updatedContent.replace(
    /http:\/\/[0-9.]+(:\d+)/g,
    (match, port) => `http://${localIp}${port}`
  );

  if (content !== updatedContent) {
    fs.writeFileSync(backendEnvPath, updatedContent);
    console.log(`✅ Updated backend/.env: BACKEND_URL and CORS_ORIGINS to ${localIp}`);
  } else {
    console.log(`ℹ️ backend/.env is already up to date (${localIp})`);
  }
}

