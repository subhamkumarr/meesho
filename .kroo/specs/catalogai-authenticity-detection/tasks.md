# Implementation Plan

- [x] 1. Initialize project structure and configuration
  - Create complete directory structure as specified in the architecture
  - Set up .gitignore, .gitattributes, and LICENSE files
  - Create .env.example with all required environment variables
  - Initialize package.json for frontend and requirements.txt for backend
  - _Requirements: 5.1, 5.2_

- [x] 2. Set up backend foundation and configuration
  - [x] 2.1 Implement configuration management system
    - Create config.py with Settings class using Pydantic for environment variable loading
    - Add validation for threshold values and file size limits
    - Include default values for all configuration parameters
    - _Requirements: 2.2, 5.5_

  - [x] 2.2 Set up database models and connection
    - Implement db.py with SQLModel engine and session management
    - Create models.py with Scan and Thresholds SQLModel entities
    - Add database initialization and table creation functions
    - _Requirements: 3.1, 3.3_

  - [x] 2.3 Create API schemas and validation
    - Implement schemas.py with Pydantic models for request/response validation
    - Define ScanCreate, ScanOut, ThresholdsIn, and ThresholdsOut schemas
    - Add file upload validation and error response schemas
    - _Requirements: 4.2, 4.3_

- [x] 3. Implement core ML pipeline components
  - [x] 3.1 Build feature extraction engine
    - Create pipeline/features.py with extract_features function
    - Implement edge detection using OpenCV Canny and Laplacian
    - Add color histogram analysis and entropy calculations
    - Implement JPEG compression artifact detection via DCT analysis
    - Add noise estimation using wavelet decomposition
    - Include texture periodicity analysis using FFT
    - Add image preprocessing (resize, format conversion, error handling)
    - _Requirements: 6.1, 6.3_

  - [x] 3.2 Implement classification system
    - Create pipeline/classifier.py with train and predict functions
    - Implement SVM classifier with RBF kernel and probability calibration
    - Add model persistence using joblib for model and scaler
    - Implement threshold-based label mapping (authentic/suspicious/synthetic)
    - Add automatic model loading with lazy initialization
    - _Requirements: 6.2, 2.4_

  - [x] 3.3 Build explanation engine
    - Create pipeline/reasons.py with reasons_from_features function
    - Map feature anomalies to human-readable explanations
    - Implement contextual reasoning based on classification confidence
    - Add actionable improvement suggestions for each classification type
    - _Requirements: 6.3, 8.1, 8.2, 8.3_

- [x] 4. Create seed data generation system
  - [x] 4.1 Implement synthetic image generator
    - Create data/seeds/synth_make.py for generating synthetic-looking images
    - Generate procedural patterns with uniform lighting
    - Create over-smoothed textures and artificial gradients
    - Produce images with minimal noise characteristics
    - _Requirements: 6.4_

  - [x] 4.2 Implement realistic image generator
    - Create data/seeds/real_make.py for generating authentic-looking images
    - Add natural lighting variations and realistic textures
    - Implement camera noise simulation and perspective distortions
    - Generate images with natural compression artifacts
    - _Requirements: 6.4_

  - [x] 4.3 Build training data pipeline
    - Create data/seeds/seed_run.py to orchestrate data generation
    - Generate balanced dataset (60 synthetic, 60 authentic samples)
    - Extract features and create labeled training dataset
    - Save training data in format suitable for classifier training
    - _Requirements: 6.4, 2.4_

- [x] 5. Implement backend API endpoints
  - [x] 5.1 Create health check endpoint
    - Implement routers/health.py with GET /health endpoint
    - Return system status and model availability
    - Add basic system diagnostics
    - _Requirements: 4.1_

  - [x] 5.2 Build image scanning endpoints
    - Create routers/scans.py with POST /scan endpoint for multi-file upload
    - Implement file validation (size, format, corruption checks)
    - Add parallel processing for multiple images
    - Integrate with ML pipeline for feature extraction and classification
    - Store scan results in database with full metadata
    - Return structured results with scores, labels, and explanations
    - Add GET /scans endpoint for paginated scan history
    - _Requirements: 1.1, 1.2, 1.3, 3.1, 3.2_

  - [x] 5.3 Implement admin management endpoints
    - Create routers/admin.py with threshold management endpoints
    - Add GET /admin/thresholds to retrieve current threshold values
    - Implement PUT /admin/thresholds for updating classification thresholds
    - Add POST /admin/train endpoint for model retraining
    - Include validation and error handling for admin operations
    - _Requirements: 2.1, 2.2, 2.3, 2.4_

- [x] 6. Set up FastAPI application
  - [x] 6.1 Create main application entry point
    - Implement main.py with FastAPI app initialization
    - Mount all routers with appropriate prefixes
    - Configure CORS for frontend integration
    - Add OpenAPI documentation configuration
    - Include startup event for model initialization
    - Add middleware for logging and error handling
    - _Requirements: 4.1, 4.4, 5.3_

  - [x] 6.2 Add backend testing suite
    - Create tests/test_health.py for health endpoint testing
    - Implement tests/test_features.py for feature extraction validation
    - Add tests for deterministic behavior and vector shape consistency
    - Include integration tests for API endpoints
    - _Requirements: 7.1, 7.2_

- [x] 7. Build frontend foundation
  - [x] 7.1 Set up Next.js project structure
    - Create package.json with all required dependencies
    - Set up TypeScript configuration with strict type checking
    - Configure TailwindCSS and shadcn/ui components
    - Add ESLint and Prettier configuration
    - Create next.config.mjs with proper build settings
    - _Requirements: 7.1, 7.3_

  - [x] 7.2 Implement API client and types
    - Create app/api.ts with centralized Axios client
    - Define TypeScript interfaces for all API requests and responses
    - Add error handling and retry logic
    - Configure base URL from environment variables
    - Include request/response interceptors for logging
    - _Requirements: 4.2, 4.3_

  - [x] 7.3 Create shared UI components
    - Implement components/ScoreBadge.tsx with color-coded authenticity indicators
    - Create components/Navbar.tsx with navigation between pages
    - Add loading states and error boundary components
    - Implement responsive design patterns
    - _Requirements: 8.1, 8.2, 8.3_

- [x] 8. Implement core frontend pages
  - [x] 8.1 Build image upload interface
    - Create app/page.tsx with drag-and-drop upload functionality
    - Implement components/Uploader.tsx with multi-file support
    - Add real-time upload progress and preview thumbnails
    - Display classification results in structured table format
    - Include error handling for upload failures and file validation
    - Show actionable guidance based on classification results
    - _Requirements: 1.1, 1.2, 1.3, 8.1, 8.2, 8.3, 8.4_

  - [x] 8.2 Create admin threshold management page
    - Implement app/admin/page.tsx for threshold configuration
    - Create components/ThresholdEditor.tsx with real-time preview
    - Add sample image testing with live classification updates
    - Include model retraining interface with progress feedback
    - Display current model metrics and performance statistics
    - _Requirements: 2.1, 2.2, 2.3, 2.4_

  - [x] 8.3 Build scan history audit page
    - Create app/scans/page.tsx with paginated scan history
    - Implement infinite scroll or pagination for performance
    - Add filtering and search capabilities
    - Display detailed scan information including reasoning
    - Include export functionality for audit records
    - _Requirements: 3.1, 3.2, 3.3, 3.4_

- [x] 9. Set up containerization and deployment
  - [x] 9.1 Create backend Docker configuration
    - Write backend/Dockerfile with Python 3.11-slim base
    - Optimize layers for caching and minimal image size
    - Add health check configuration
    - Include volume mounts for model persistence
    - _Requirements: 5.1, 5.4_

  - [x] 9.2 Create frontend Docker configuration
    - Write frontend/Dockerfile with Node 20-alpine base
    - Implement multi-stage build for production optimization
    - Configure static file serving and routing
    - Add health check for frontend service
    - _Requirements: 5.1, 5.4_

  - [x] 9.3 Implement Docker Compose orchestration
    - Create ops/docker-compose.yml with backend and frontend services
    - Configure service networking and port mapping
    - Add volume mounts for data persistence
    - Include environment variable configuration
    - Add health checks and restart policies
    - _Requirements: 5.1, 5.2, 5.4_

- [x] 10. Add development and deployment scripts
  - [x] 10.1 Create development setup scripts
    - Write ops/dev_setup.sh for local development environment
    - Create Python virtual environment and install dependencies
    - Run initial model training with seed data
    - Set up frontend dependencies and build tools
    - _Requirements: 5.5_

  - [x] 10.2 Create local run scripts
    - Implement ops/run_local.sh for non-Docker development
    - Start backend server with hot reloading
    - Launch frontend development server
    - Include environment variable setup
    - _Requirements: 5.5_

- [x] 11. Implement CI/CD pipeline
  - [x] 11.1 Set up GitHub Actions workflow
    - Create .github/workflows/ci.yml for automated testing
    - Add Python linting with ruff and type checking
    - Include pytest execution for backend tests
    - Add frontend linting with ESLint and type checking with TypeScript
    - Include build verification for both services
    - _Requirements: 7.1, 7.2, 7.3, 7.4_

- [x] 12. Create documentation and final polish
  - [x] 12.1 Write comprehensive README
    - Document project overview and quick start instructions
    - Include both Docker and non-Docker setup procedures
    - Document all environment variables and configuration options
    - Add API endpoint documentation and usage examples
    - Explain detection algorithm and feature extraction approach
    - Include troubleshooting guide and common issues
    - _Requirements: 4.1_

  - [x] 12.2 Create operational runbook
    - Write RUNBOOK.md with deployment and maintenance procedures
    - Document model retraining and threshold adjustment processes
    - Include monitoring and logging guidance
    - Add backup and recovery procedures
    - Document performance tuning and scaling considerations
    - _Requirements: 2.4, 6.4_

  - [x] 12.3 Add final testing and validation




    - Verify complete docker compose up --build workflow
    - Test all user workflows end-to-end
    - Validate API documentation accuracy
    - Ensure all error handling paths work correctly
    - Verify responsive design across different screen sizes
    - _Requirements: 5.1, 5.2, 7.4, 8.5_