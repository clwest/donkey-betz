// Jest configuration for frontend JavaScript tests
module.exports = {
  testEnvironment: 'jsdom',
  rootDir: '../../',
  testMatch: [
    '<rootDir>/tests/frontend/**/*.test.js',
  ],
  moduleNameMapper: {
    // Map static file imports
    '\\.(css|less|scss|sass)$': '<rootDir>/tests/frontend/__mocks__/styleMock.js',
    '\\.(gif|ttf|eot|svg|png)$': '<rootDir>/tests/frontend/__mocks__/fileMock.js',
  },
  setupFilesAfterEnv: ['<rootDir>/tests/frontend/setup.js'],
  collectCoverageFrom: [
    'core/static/js/**/*.js',
    '!core/static/js/vendor/**',
  ],
  coverageDirectory: '<rootDir>/coverage/frontend',
  coverageReporters: ['text', 'lcov', 'html'],
  testTimeout: 10000,
};
