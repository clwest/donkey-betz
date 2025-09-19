#!/usr/bin/env node

/**
 * Fix Frontend API Configuration Script
 * Updates all service files to use correct API v1 endpoints
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { dirname } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Configuration fixes to apply
const ENDPOINT_FIXES = {
  // Old -> New endpoint mappings
  '/api/agents/': '/api/v1/agents/',
  '/v1/agents/': '/api/v1/agents/',
  '/api/v1/agents/agents/': '/api/v1/agents/', // Fix double agents
  'localhost:8001': 'localhost:8000', // Fix wrong port
  'localhost:8002': 'localhost:8000', // Fix wrong port
  '0ef9dd74312961574231b1c573d8af0cba3ea0f4': '0fb2390dedd5cc47ec7e6a320e1477b31b7c0a97', // Fix token
};

// Files and directories to check
const TARGET_PATHS = [
  'src/services',
  'src/components',
  'src/pages',
  'src/features',
  'src/store'
];

let filesFixed = 0;
let totalChanges = 0;

function fixFile(filePath) {
  let content = fs.readFileSync(filePath, 'utf8');
  let originalContent = content;
  let changes = 0;
  
  // Apply all fixes
  for (const [oldValue, newValue] of Object.entries(ENDPOINT_FIXES)) {
    const regex = new RegExp(escapeRegExp(oldValue), 'g');
    const matches = content.match(regex);
    if (matches) {
      content = content.replace(regex, newValue);
      changes += matches.length;
      console.log(`  ✓ Fixed ${matches.length} occurrence(s) of: ${oldValue} → ${newValue}`);
    }
  }
  
  // Fix specific API patterns
  content = content.replace(/\/api\/v1\/agents\/templates\//g, '/api/v1/agents/templates/');
  content = content.replace(/\/api\/v1\/agents\/execute\//g, '/api/v1/agents/execute/');
  content = content.replace(/\/api\/v1\/agents\/executions\//g, '/api/v1/agents/executions/');
  
  if (content !== originalContent) {
    fs.writeFileSync(filePath, content, 'utf8');
    filesFixed++;
    totalChanges += changes;
    console.log(`📝 Fixed ${filePath}`);
    return true;
  }
  return false;
}

function escapeRegExp(string) {
  return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

function walkDir(dir) {
  const files = fs.readdirSync(dir);
  
  for (const file of files) {
    const fullPath = path.join(dir, file);
    const stat = fs.statSync(fullPath);
    
    if (stat.isDirectory() && !file.includes('node_modules')) {
      walkDir(fullPath);
    } else if (stat.isFile() && (
      file.endsWith('.ts') || 
      file.endsWith('.tsx') || 
      file.endsWith('.js') || 
      file.endsWith('.jsx')
    )) {
      fixFile(fullPath);
    }
  }
}

console.log('🔧 Fixing Frontend API Configuration...\n');

// Process all target paths
for (const targetPath of TARGET_PATHS) {
  const fullPath = path.resolve(targetPath);
  if (fs.existsSync(fullPath)) {
    console.log(`\n📂 Checking ${targetPath}/...`);
    walkDir(fullPath);
  }
}

console.log('\n' + '='.repeat(50));
console.log(`✅ Fixed ${filesFixed} files with ${totalChanges} total changes`);
console.log('='.repeat(50));

// Additional recommendations
console.log('\n📋 Next Steps:');
console.log('1. Restart the frontend dev server: npm run dev');
console.log('2. Clear browser cache and localStorage');
console.log('3. Test the Command Center at http://localhost:5173/control-center');
console.log('\n🚀 Your frontend is now configured to use the correct API endpoints!');
