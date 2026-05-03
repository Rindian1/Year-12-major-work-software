# Year 12 Software Engineering Project - Part B Task Description

## Project Overview
Part B focuses on transforming the Term 4 Flask web application into a secure, automated, and production-ready system. This involves implementing machine learning automation, addressing security vulnerabilities, improving code quality, and deploying the application to a live hosting environment.

## Part B Requirements - Secure Development, Automation & Deployment (25 Marks)

### 6. Automation Functionality (5 Marks)

#### 6.1 Regression Model Execution (3 marks)
- **Model Implementation**: Integrate a regression model (Linear, Logistic, or Polynomial) using appropriate Python libraries (scikit-learn recommended)
- **Data Processing**: The automation feature must successfully process the provided dataset without crashes or server errors
- **Error Handling**: Implement robust error handling for edge cases in data processing and model execution
- **Model Validation**: Ensure the model works with real data from your application's domain

#### 6.2 Output Accuracy & Relevance (2 marks)
- **Logical Predictions**: Generate meaningful predictions, classifications, or automated outputs that align with the application's purpose
- **Utility Enhancement**: The automation feature must genuinely enhance the application's functionality and solve the objective defined in Part A
- **User Value**: Provide actionable insights or automated processes that benefit the end-user
- **Result Validation**: Ensure outputs are accurate and relevant to the application's context

### 7. Web Integration (5 Marks)

#### 7.1 Flask Routing & Data Handling (3 marks)
- **Secure Data Flow**: Implement secure data transmission from web forms to Python backend and back
- **Route Architecture**: Design logically structured route handlers that appropriately manage GET/POST requests
- **Data Validation**: Implement proper input validation and sanitization for all user inputs
- **Session Management**: Handle user sessions and state management securely
- **API Design**: Create clean, RESTful endpoints for the automation functionality

#### 7.2 Seamless UI Integration (2 marks)
- **Natural Extension**: Ensure the automation feature feels like a natural part of the existing Term 4 application
- **Dynamic Rendering**: Display model predictions and automated results dynamically in the user interface
- **User Experience**: Provide a smooth, intuitive user experience when interacting with automation features
- **Visual Feedback**: Include appropriate loading states, progress indicators, and result presentations
- **Responsive Design**: Ensure automation features work across different screen sizes and devices

### 8. Secure Architecture (5 Marks)

#### 8.1 Security Patch Implementation (3 marks)
- **Vulnerability Remediation**: Successfully patch all security vulnerabilities identified in Part A
- **OWASP Compliance**: Implement robust mitigations following OWASP security guidelines
- **SQL Injection Prevention**: Implement parameterized queries or ORM to prevent SQLi attacks
- **Safe Data Handling**: Ensure all data processing follows security best practices
- **Input Sanitization**: Implement comprehensive input validation and sanitization
- **Authentication Security**: Secure user authentication and authorization mechanisms

#### 8.2 Testing Evidence (2 marks)
- **SAST/DAST Documentation**: Provide clear evidence of Static and Dynamic Application Security Testing
- **GitHub Commits**: Demonstrate security evolution through specific, descriptive GitHub commit messages
- **Code Comments**: Include detailed code comments explaining security patches and implementations
- **Testing Reports**: Document security testing results and remediation steps
- **Vulnerability Scans**: Show evidence of vulnerability scanning tools and their results

### 9. Code Quality (5 Marks)

#### 9.1 Code Readability & Comments (3 marks)
- **Security Documentation**: Excellent comments explaining complex security implementations
- **ML Logic Explanation**: Clear documentation of mathematical logic and machine learning integration
- **Code Structure**: Well-organized code with logical separation of concerns
- **Function Documentation**: Comprehensive docstrings for all functions and classes
- **Inline Comments**: Meaningful inline comments for complex algorithms and security measures

#### 9.2 Standards & Cleanup (2 marks)
- **PEP 8 Compliance**: Strict adherence to Python PEP 8 formatting standards
- **Code Refactoring**: Remove redundant, messy, or insecure legacy code from Term 4 build
- **Import Organization**: Clean and organized import statements
- **Variable Naming**: Use descriptive variable names following Python conventions
- **Code Optimization**: Refactor inefficient code patterns and improve performance

### 10. Deployment & Presentation (5 Marks)

#### 10.1 Live Hosting (2 marks)
- **PythonAnywhere Deployment**: Successfully deploy the upgraded Flask application to PythonAnywhere
- **Full Functionality**: Ensure all features work correctly in the live environment
- **Live URL Accessibility**: Provide a working, accessible URL for the deployed application
- **Environment Configuration**: Proper configuration of production environment variables
- **Database Setup**: Ensure database connectivity and functionality in production

#### 10.2 Digital and Printed Presentation (2 marks)
- **Documentation Standards**: Complete project documentation with spelling and grammar check
- **Professional Formatting**: Include table of contents, headers, footers, headings, and subheadings
- **Visual Elements**: Incorporate screenshots, tables, and appropriate visuals
- **Word Document Format**: Submit as a single, well-formatted Word document
- **Printed Binding**: Provide a professionally printed and bound document

#### 10.3 GitHub README.md (1 mark)
- **Setup Instructions**: Clear instructions on how to access and use the application
- **Security Summary**: Brief "Security Patch & Automation Notes" section for users
- **Installation Guide**: Step-by-step setup instructions for developers
- **Feature Documentation**: Description of key features and automation capabilities
- **Contact Information**: Appropriate contact details and project information

## Part B Specific Deliverables

### Security & Automation Documentation
1. **Security Patch Report**
   - Detailed description of vulnerabilities identified in Part A
   - Step-by-step documentation of security fixes implemented
   - Evidence of SAST/DAST testing with before/after comparisons
   - GitHub commit history showing security evolution

2. **Machine Learning Integration Report**
   - Regression model selection rationale and implementation details
   - Dataset processing and validation procedures
   - Model performance metrics and accuracy analysis
   - Integration documentation showing how ML enhances the application

3. **Updated Project Documentation**
   - Complete documentation from Part A with security and automation additions
   - Professional formatting with table of contents, headers, footers
   - Screenshots of new automation features and security implementations
   - Deployment documentation and live URL information

### Code & Deployment Artifacts
1. **Refactored Source Code**
   - Clean, PEP 8 compliant Python/Flask application
   - Comprehensive comments explaining security and ML implementations
   - Removed legacy insecure code patterns
   - Well-structured modular architecture

2. **Deployed Application**
   - Fully functional Flask application on PythonAnywhere
   - Live URL accessible for evaluation
   - Production-ready configuration
   - Database connectivity and functionality verified

3. **GitHub Repository**
   - Complete source code with meaningful commit messages
   - Comprehensive README.md with setup instructions
   - Security Patch & Automation Notes section
   - Proper version control throughout development

4. **Testing Evidence**
   - Security testing results and remediation evidence
   - Machine learning model validation and testing
   - Integration testing for web automation features
   - User acceptance testing documentation

## Part B Assessment Breakdown (25 Marks Total)

### Automation Functionality (5 Marks - 20%)
- **Model Execution (3 marks)**: Successful regression model implementation with robust error handling
- **Output Quality (2 marks)**: Accurate, relevant predictions that enhance application utility

### Web Integration (5 Marks - 20%)
- **Backend Integration (3 marks)**: Secure Flask routing and data handling
- **Frontend Integration (2 marks)**: Seamless UI integration with dynamic result rendering

### Secure Architecture (5 Marks - 20%)
- **Security Implementation (3 marks)**: Complete vulnerability remediation with OWASP compliance
- **Testing Evidence (2 marks)**: Documented SAST/DAST testing and security evolution

### Code Quality (5 Marks - 20%)
- **Documentation (3 marks)**: Excellent comments explaining security and ML implementations
- **Standards Compliance (2 marks)**: PEP 8 compliance and code cleanup

### Deployment & Presentation (5 Marks - 20%)
- **Live Deployment (2 marks)**: Functional PythonAnywhere hosting
- **Documentation (2 marks)**: Professional formatted Word document with all requirements
- **GitHub README (1 mark)**: Comprehensive setup and usage instructions

## Part B Implementation Timeline

### Week 1-2: Security Audit & Planning
- Conduct comprehensive security vulnerability assessment
- Plan regression model integration approach
- Design secure architecture improvements
- Set up development and testing environments

### Week 3-4: Security Implementation
- Implement SQL injection prevention measures
- Add input validation and sanitization
- Secure authentication and session management
- Conduct SAST/DAST testing and document results

### Week 5-7: Machine Learning Integration
- Select and implement appropriate regression model
- Develop data processing pipeline
- Integrate ML model with Flask backend
- Create API endpoints for automation features

### Week 8-9: Frontend Integration
- Design and implement automation UI components
- Add dynamic result rendering
- Implement loading states and error handling
- Ensure responsive design compatibility

### Week 10-11: Code Quality & Refactoring
- Refactor code to PEP 8 standards
- Add comprehensive comments and documentation
- Remove legacy insecure code
- Optimize performance and structure

### Week 12: Testing & Validation
- Comprehensive integration testing
- Machine learning model validation
- Security testing verification
- User acceptance testing

### Week 13-14: Deployment
- Configure PythonAnywhere environment
- Deploy application to production
- Verify all functionality in live environment
- Performance optimization

### Week 15-16: Documentation & Final Submission
- Complete project documentation
- Create professional Word document
- Prepare GitHub README.md
- Final testing and submission preparation

## Technical Requirements & Constraints

### Mandatory Technologies
- **Backend**: Python with Flask framework
- **Machine Learning**: scikit-learn for regression models
- **Database**: Secure database implementation with parameterized queries
- **Hosting**: PythonAnywhere for live deployment
- **Version Control**: GitHub with meaningful commit messages

### Security Requirements
- **OWASP Compliance**: Follow OWASP security guidelines
- **SQL Injection Prevention**: Use parameterized queries or ORM
- **Input Validation**: Comprehensive input sanitization
- **Authentication**: Secure user authentication mechanisms
- **Data Protection**: Safe data handling and storage practices

### Code Quality Standards
- **PEP 8 Compliance**: Strict adherence to Python formatting standards
- **Documentation**: Comprehensive comments and docstrings
- **Error Handling**: Robust error handling throughout application
- **Testing**: Evidence of security and functionality testing

### Documentation Standards
- **Professional Formatting**: Table of contents, headers, footers
- **Visual Elements**: Screenshots, tables, diagrams
- **Security Evidence**: Before/after security testing documentation
- **ML Documentation**: Model selection and implementation details

## Success Criteria

### Functional Success
- All security vulnerabilities from Part A successfully remediated
- Machine learning model provides accurate, relevant predictions
- Web application functions seamlessly with automation features
- Live deployment fully operational on PythonAnywhere

### Technical Success
- Code achieves 100% PEP 8 compliance
- Zero critical security vulnerabilities in final application
- Machine learning integration enhances application utility
- Comprehensive testing evidence documented

### Documentation Success
- Professional Word document with all required elements
- GitHub README with clear setup instructions
- Security patch documentation with testing evidence
- Complete project documentation from Part A updated

---

*This task description provides a comprehensive roadmap for Part B implementation, focusing on security hardening, machine learning integration, and production deployment of the Flask web application.*

---

*Note: This task description should be adapted based on the specific requirements outlined in Part B of your assessment notification. Please review the official assessment document and modify this template accordingly.*
