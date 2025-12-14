# Serverless Web Application Architecture

## Architecture Overview

```
┌─────────────┐    ┌──────────────┐    ┌─────────────┐
│   Web User  │───▶│  CloudFront  │───▶│ S3 Bucket   │
│   Browser   │    │     CDN      │    │ Static Site │
└─────────────┘    └──────────────┘    └─────────────┘
       │
       │ API Calls
       ▼
┌─────────────┐    ┌──────────────┐    ┌─────────────┐
│ API Gateway │───▶│   Lambda     │───▶│  DynamoDB   │
│   REST API  │    │  Functions   │    │   Tables    │
└─────────────┘    └──────────────┘    └─────────────┘
```

## Components

### Frontend Layer
- **CloudFront CDN**: Global content delivery network for fast static asset delivery
- **S3 Static Website**: Hosts HTML, CSS, JavaScript files for the web application

### API Layer  
- **API Gateway**: Managed REST API service that handles HTTP requests
  - Authentication and authorization
  - Request/response transformation
  - Rate limiting and throttling
  - CORS handling

### Compute Layer
- **Lambda Functions**: Serverless compute for business logic
  - **User Service**: Handles user registration, profile management
  - **Data Service**: Processes application data operations
  - **Auth Service**: Manages authentication and session handling

### Database Layer
- **DynamoDB Tables**: NoSQL database for scalable data storage
  - **Users Table**: User profiles and account information
  - **Application Data**: Core business data
  - **User Sessions**: Authentication tokens and session data

## Data Flow

1. **Static Content**: User browser → CloudFront → S3 → Static assets served
2. **API Requests**: User browser → API Gateway → Lambda Functions → DynamoDB
3. **Responses**: DynamoDB → Lambda Functions → API Gateway → User browser

## Benefits

- **Serverless**: No server management, automatic scaling
- **Cost-effective**: Pay only for actual usage
- **High availability**: Built-in redundancy across AWS regions
- **Performance**: Global CDN and managed services
- **Security**: AWS IAM integration and managed security features

## Typical Use Cases

- Single Page Applications (SPAs)
- Mobile app backends
- Microservices APIs
- Real-time web applications
- E-commerce platforms