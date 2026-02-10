# AGENTS.md

## Project Overview
This is a web archive project built with Node.js, Express, and React. The project consists of a backend API server and a frontend application for managing and viewing archived web content.

## Development Commands

### Backend (Node.js/Express)
- **Install dependencies**: `npm install`
- **Start development server**: `npm run dev` (runs with nodemon)
- **Start production server**: `npm start`
- **Run tests**: `npm test`
- **Run specific test**: `npm test -- --grep "test name"`
- **Lint code**: `npm run lint`
- **Fix linting issues**: `npm run lint:fix`

### Frontend (React)
- **Install dependencies**: `cd client && npm install`
- **Start development server**: `cd client && npm start`
- **Build for production**: `cd client && npm run build`
- **Run tests**: `cd client && npm test`
- **Run specific test**: `cd client && npm test -- --testNamePattern="test name"`
- **Lint code**: `cd client && npm run lint`
- **Fix linting issues**: `cd client && npm run lint:fix`

## Code Style Guidelines

### General Principles
- Use modern JavaScript/ES6+ features
- Keep functions small and focused on single responsibility
- Use meaningful variable and function names
- Add JSDoc comments for complex functions
- Follow DRY (Don't Repeat Yourself) principle

### Import/Export Conventions
```javascript
// Use named exports for utilities
export const formatDate = (date) => { ... };

// Use default export for main components/modules
export default class ArchiveService { ... };

// Import order:
// 1. Node.js built-in modules
// 2. Third-party dependencies
// 3. Local modules (relative imports)
const fs = require('fs');
const express = require('express');
const { ArchiveService } = require('./services/archive');
```

### Error Handling
```javascript
// Use async/await with try-catch
try {
  const result = await archiveService.save(data);
  return res.json(result);
} catch (error) {
  console.error('Archive save error:', error);
  return res.status(500).json({ error: 'Failed to save archive' });
}

// Create custom error classes
class ArchiveError extends Error {
  constructor(message, code) {
    super(message);
    this.name = 'ArchiveError';
    this.code = code;
  }
}
```

### Naming Conventions
- **Variables**: camelCase (`const archiveData = ...`)
- **Functions**: camelCase (`const formatDate = ...`)
- **Classes**: PascalCase (`class ArchiveService`)
- **Constants**: UPPER_SNAKE_CASE (`const MAX_FILE_SIZE = ...`)
- **Files**: kebab-case (`archive-service.js`)
- **Directories**: kebab-case (`api-routes/`)

### TypeScript/JavaScript Types
```javascript
// Use JSDoc for type hints in JavaScript
/**
 * @typedef {Object} ArchiveItem
 * @property {string} id - Unique identifier
 * @property {string} url - Original URL
 * @property {Date} createdAt - Creation timestamp
 */

/**
 * Saves archive data to database
 * @param {ArchiveItem} data - Archive data to save
 * @returns {Promise<ArchiveItem>} Saved archive item
 */
async function saveArchive(data) { ... }
```

### React Component Guidelines
```javascript
// Use functional components with hooks
const ArchiveList = ({ archives, onSelect }) => {
  const [loading, setLoading] = useState(false);
  
  useEffect(() => {
    fetchArchives();
  }, []);

  return (
    <div className="archive-list">
      {archives.map(archive => (
        <ArchiveItem 
          key={archive.id} 
          archive={archive}
          onClick={() => onSelect(archive)}
        />
      ))}
    </div>
  );
};

// PropTypes for type checking
ArchiveList.propTypes = {
  archives: PropTypes.array.isRequired,
  onSelect: PropTypes.func.isRequired
};
```

### API Response Format
```javascript
// Success response
{
  "success": true,
  "data": { ... },
  "message": "Operation completed successfully"
}

// Error response
{
  "success": false,
  "error": "Error description",
  "code": "ERROR_CODE"
}
```

### Database/MongoDB Guidelines
```javascript
// Use Mongoose schemas with validation
const archiveSchema = new mongoose.Schema({
  url: { 
    type: String, 
    required: true,
    validate: {
      validator: function(v) {
        return /^https?:\/\/.+/.test(v);
      },
      message: 'URL must be valid'
    }
  },
  title: { type: String, required: true },
  content: { type: String, required: true },
  createdAt: { type: Date, default: Date.now }
});

// Use lean queries for performance
const archives = await Archive.find({}).lean().exec();
```

### Environment Configuration
```javascript
// Use .env files for configuration
const PORT = process.env.PORT || 3000;
const MONGODB_URI = process.env.MONGODB_URI || 'mongodb://localhost:27017/archive';

// Validate required environment variables
const requiredEnvVars = ['MONGODB_URI', 'JWT_SECRET'];
requiredEnvVars.forEach(varName => {
  if (!process.env[varName]) {
    throw new Error(`Missing required environment variable: ${varName}`);
  }
});
```

### Testing Guidelines
```javascript
// Use Jest for unit/integration tests
describe('ArchiveService', () => {
  test('should save archive successfully', async () => {
    const mockData = { url: 'https://example.com', title: 'Test' };
    const result = await archiveService.save(mockData);
    
    expect(result).toHaveProperty('id');
    expect(result.url).toBe(mockData.url);
  });
});

// Use supertest for API testing
describe('Archive API', () => {
  test('POST /api/archives should create archive', async () => {
    const response = await request(app)
      .post('/api/archives')
      .send({ url: 'https://example.com' })
      .expect(201);
      
    expect(response.body.success).toBe(true);
  });
});
```

### Security Best Practices
- Validate all user inputs
- Use parameterized queries to prevent SQL injection
- Implement rate limiting for API endpoints
- Use HTTPS in production
- Sanitize user-generated content
- Implement proper authentication/authorization

### Performance Optimization
- Use database indexes for frequently queried fields
- Implement caching for expensive operations
- Use pagination for large datasets
- Optimize images and static assets
- Use lazy loading for React components
- Implement proper error boundaries

## Git Workflow
- Use feature branches: `feature/archive-search`
- Write descriptive commit messages: `feat: add search functionality to archives`
- Create pull requests for code review
- Use conventional commits: `feat:`, `fix:`, `docs:`, `style:`, `refactor:`

## Deployment
- Use Docker containers for consistent deployment
- Implement health checks for monitoring
- Use environment-specific configurations
- Log important events and errors
- Implement proper backup strategies