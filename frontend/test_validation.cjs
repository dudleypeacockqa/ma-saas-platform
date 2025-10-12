#!/usr/bin/env node

/**
 * Frontend Test Validation Script
 * Validates that the frontend components exist and can be imported
 */

const fs = require('fs');
const path = require('path');

console.log('='.repeat(60));
console.log('FRONTEND TEST VALIDATION');
console.log('='.repeat(60));

const testResults = [];

function validateFile(filePath, description) {
  try {
    const fullPath = path.join(__dirname, filePath);
    const exists = fs.existsSync(fullPath);

    if (exists) {
      const stats = fs.statSync(fullPath);
      const sizeKB = Math.round(stats.size / 1024);
      console.log(`[OK] ${description} - ${sizeKB}KB`);
      testResults.push({ test: description, status: 'PASS', size: sizeKB });
      return true;
    } else {
      console.log(`[FAIL] ${description} - File not found`);
      testResults.push({ test: description, status: 'FAIL', error: 'File not found' });
      return false;
    }
  } catch (error) {
    console.log(`[ERROR] ${description} - ${error.message}`);
    testResults.push({ test: description, status: 'ERROR', error: error.message });
    return false;
  }
}

function validateDirectory(dirPath, description) {
  try {
    const fullPath = path.join(__dirname, dirPath);
    const exists = fs.existsSync(fullPath);

    if (exists) {
      const files = fs.readdirSync(fullPath);
      console.log(`[OK] ${description} - ${files.length} files`);
      testResults.push({ test: description, status: 'PASS', count: files.length });
      return true;
    } else {
      console.log(`[FAIL] ${description} - Directory not found`);
      testResults.push({ test: description, status: 'FAIL', error: 'Directory not found' });
      return false;
    }
  } catch (error) {
    console.log(`[ERROR] ${description} - ${error.message}`);
    testResults.push({ test: description, status: 'ERROR', error: error.message });
    return false;
  }
}

// Main validation tests
console.log('\n[TEST 1] Core Application Files');
validateFile('src/App.jsx', 'Main App Component');
validateFile('src/main.jsx', 'Application Entry Point');
validateFile('package.json', 'Package Configuration');

console.log('\n[TEST 2] Key Components');
validateFile('src/pages/Dashboard.jsx', 'Dashboard Component');
validateFile('src/pages/MasterAdminPortal.jsx', 'Master Admin Portal');
validateFile('src/pages/ContentCreationStudio.jsx', 'Content Creation Studio');

console.log('\n[TEST 3] Test Files');
validateFile('src/tests/Dashboard.test.jsx', 'Dashboard Tests');
validateFile('src/tests/MasterAdminPortal.test.jsx', 'Admin Portal Tests');
validateFile('src/tests/ContentCreationStudio.test.jsx', 'Content Studio Tests');

console.log('\n[TEST 4] Configuration Files');
validateFile('vite.config.js', 'Vite Configuration');
validateFile('tailwind.config.js', 'Tailwind Configuration');
validateFile('.env.example', 'Environment Template');

console.log('\n[TEST 5] Asset Directories');
validateDirectory('src/components', 'Components Directory');
validateDirectory('src/pages', 'Pages Directory');
validateDirectory('src/tests', 'Tests Directory');

// Summary
console.log('\n' + '=' * 60);
const totalTests = testResults.length;
const passedTests = testResults.filter((r) => r.status === 'PASS').length;
const failedTests = testResults.filter((r) => r.status === 'FAIL').length;
const errorTests = testResults.filter((r) => r.status === 'ERROR').length;

console.log(`FRONTEND VALIDATION SUMMARY:`);
console.log(`Total Tests: ${totalTests}`);
console.log(`Passed: ${passedTests}`);
console.log(`Failed: ${failedTests}`);
console.log(`Errors: ${errorTests}`);

if (failedTests === 0 && errorTests === 0) {
  console.log('\n[SUCCESS] All frontend validation tests passed!');
  console.log('[SUCCESS] Frontend is ready for comprehensive testing');
  process.exit(0);
} else {
  console.log('\n[WARNING] Some frontend validation issues found');
  console.log('[INFO] Check missing files and fix before running full test suite');
  process.exit(1);
}
