# Next Wave 🌊

**Navigate the currents of your career journey**

Next Wave is an AI-powered career pathway advisor that helps students discover personalized educational roadmaps from Associate's degrees through professional careers. Built at **SharkByte**, a 36-hour hackathon hosted by Miami Dade College.

## Mission Statement

Next Wave empowers students to navigate their career journey by providing personalized, data-driven educational pathways. We bridge the gap between career aspirations and educational planning, making it easier for students to understand their options, plan their academic journey, and achieve their professional goals.

## Features

- **Interactive Career Wizard**: Step-by-step interface to explore career pathways
- **Personalized Roadmaps**: AI-generated educational pathways tailored to each student's goals
- **Financial Planning**: Tuition, housing, and cost estimates for each degree level
- **Career Outcomes**: Entry-level and mid-career salary projections
- **PDF Export**: Download your complete roadmap for offline reference
- **Modern UI**: Beautiful, responsive design with smooth animations and intuitive navigation

## Tech Stack

### Frontend
- **React** with TypeScript
- **Tailwind CSS** for styling
- **Framer Motion** for animations
- **jsPDF** for PDF generation
- Deployed on **AWS S3** with CloudFront CDN

### Backend
- **AWS Lambda** (Python) for serverless API
- **AWS API Gateway** for REST API endpoints
- **AWS DynamoDB** for data storage:
  - `CareerPathways` - Career pathway templates
  - `MDCPrograms` - Miami Dade College program data
  - `MDCCertifications` - Certification information
  - `MDCClubs` - Student clubs and organizations
- **AWS Systems Manager Parameter Store** for secure API key management
- **Google Gemini AI** for intelligent pathway generation

## AI Agents

Next Wave uses a multi-agent architecture powered by Google Gemini AI:

1. **Agent 1 - Pathway Structure Generator**: Creates the foundational educational pathway including Associate's and Bachelor's degree programs, key courses, duration, and articulation agreements.

2. **Agent 2 - Career Outcomes Analyzer**: Generates career outcome data including entry-level and mid-career job titles with salary projections.

3. **Agent 4 - Certifications & Clubs Matcher**: Matches relevant certifications and student clubs to each career pathway by querying DynamoDB and using AI to provide personalized recommendations.

## AWS Infrastructure

- **S3**: Static website hosting for the React frontend
- **CloudFront**: Content Delivery Network for fast global content delivery
- **API Gateway**: RESTful API endpoint for the Lambda function
- **Lambda**: Serverless function handling all AI agent orchestration and data processing
- **DynamoDB**: NoSQL database storing MDC programs, certifications, and clubs data
- **Parameter Store**: Secure storage for API keys and configuration

## Getting Started

### Prerequisites
- Node.js 18+ and npm
- AWS CLI configured (for deployment)
- AWS account with appropriate permissions

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

### Environment Variables

Create a `.env` file in the root directory:

```
VITE_API_ENDPOINT=https://your-api-gateway-url.amazonaws.com/prod/pathway
```

## Project Structure

```
NextWave/
├── src/
│   ├── components/
│   │   └── CareerWizard.tsx    # Main career pathway wizard component
│   ├── App.tsx                  # Main application component
│   └── main.tsx                 # Application entry point
├── lambda_function.py           # AWS Lambda handler with AI agents
├── scripts/                     # Data processing and setup scripts
└── README.md
```

## Hackathon

Built at **SharkByte**, a 36-hour hackathon hosted by Miami Dade College. Next Wave was created to help students navigate their educational journey and make informed decisions about their career paths.

## License

This project was created for the SharkByte hackathon.
