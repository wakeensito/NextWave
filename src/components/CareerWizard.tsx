import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { ArrowLeft, ArrowRight, Sparkles, GraduationCap, MapPin, CheckCircle2, Waves, Loader2, ChevronDown, DollarSign, Briefcase, TrendingUp, Scale, Stethoscope, BookOpen, Download } from 'lucide-react';
import jsPDF from 'jspdf';

// Animated Shark Loading Component
function LoadingShark() {
  return (
    <div className="relative flex items-center justify-center">
      {/* Waves background */}
      <div className="absolute inset-0 flex items-center justify-center">
        <motion.div
          className="absolute w-32 h-32 rounded-full border-4 border-cyan-200/30"
          animate={{
            scale: [1, 1.2, 1],
            opacity: [0.3, 0.5, 0.3],
          }}
          transition={{
            duration: 2,
            repeat: Infinity,
            ease: "easeInOut",
          }}
        />
        <motion.div
          className="absolute w-24 h-24 rounded-full border-4 border-teal-200/30"
          animate={{
            scale: [1, 1.3, 1],
            opacity: [0.3, 0.5, 0.3],
          }}
          transition={{
            duration: 2,
            repeat: Infinity,
            ease: "easeInOut",
            delay: 0.3,
          }}
        />
      </div>
      
      {/* Spinning Shark */}
      <motion.div
        className="relative z-10"
        animate={{
          rotate: 360,
        }}
        transition={{
          duration: 2,
          repeat: Infinity,
          ease: "linear",
        }}
      >
        <svg
          width="80"
          height="80"
          viewBox="0 0 100 100"
          className="drop-shadow-lg"
        >
          {/* Shark body */}
          <ellipse
            cx="50"
            cy="50"
            rx="35"
            ry="20"
            fill="url(#sharkGradient)"
            className="drop-shadow-md"
          />
          {/* Shark tail */}
          <path
            d="M 15 50 Q 5 40, 5 50 Q 5 60, 15 50"
            fill="url(#sharkGradient)"
          />
          {/* Shark fin */}
          <path
            d="M 50 30 Q 60 25, 65 30 Q 60 35, 50 30"
            fill="url(#sharkGradient)"
          />
          {/* Eye */}
          <circle cx="65" cy="48" r="4" fill="white" />
          <circle cx="66" cy="47" r="2" fill="#0ea5e9" />
          {/* Mouth */}
          <path
            d="M 70 50 Q 75 52, 70 54"
            stroke="#0ea5e9"
            strokeWidth="2"
            fill="none"
          />
          {/* Gradient definition */}
          <defs>
            <linearGradient id="sharkGradient" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#06b6d4" stopOpacity="1" />
              <stop offset="50%" stopColor="#14b8a6" stopOpacity="1" />
              <stop offset="100%" stopColor="#0ea5e9" stopOpacity="1" />
            </linearGradient>
          </defs>
        </svg>
      </motion.div>
    </div>
  );
}

// Modern Accordion/Dropdown Component
interface AccordionProps {
  title: string;
  icon?: React.ReactNode;
  children: React.ReactNode;
  defaultOpen?: boolean;
  color?: string;
}

function Accordion({ title, icon, children, defaultOpen = false, color = 'cyan' }: AccordionProps) {
  const [isOpen, setIsOpen] = useState(defaultOpen);
  
  const colorClasses = {
    cyan: 'from-cyan-50 to-cyan-100/50 border-cyan-200',
    teal: 'from-teal-50 to-teal-100/50 border-teal-200',
    orange: 'from-orange-50 to-orange-100/50 border-orange-200',
    indigo: 'from-indigo-50 to-indigo-100/50 border-indigo-200',
    purple: 'from-purple-50 to-purple-100/50 border-purple-200',
    emerald: 'from-emerald-50 to-emerald-100/50 border-emerald-200',
  };

  const iconColorClasses = {
    cyan: 'text-cyan-600',
    teal: 'text-teal-600',
    orange: 'text-orange-600',
    indigo: 'text-indigo-600',
    purple: 'text-purple-600',
    emerald: 'text-emerald-600',
  };

  return (
    <div className={`mt-4 rounded-xl border bg-gradient-to-br ${colorClasses[color as keyof typeof colorClasses]} overflow-hidden transition-all duration-300`}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full px-4 py-3 flex items-center justify-between hover:bg-white/30 transition-colors duration-200"
      >
        <div className="flex items-center gap-3">
          {icon && <div className={iconColorClasses[color as keyof typeof iconColorClasses]}>{icon}</div>}
          <span className="font-semibold text-gray-800 text-sm">{title}</span>
        </div>
        <motion.div
          animate={{ rotate: isOpen ? 180 : 0 }}
          transition={{ duration: 0.3 }}
          className={iconColorClasses[color as keyof typeof iconColorClasses]}
        >
          <ChevronDown className="w-5 h-5" />
        </motion.div>
      </button>
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3, ease: 'easeInOut' }}
            className="overflow-hidden"
          >
            <div className="px-4 pb-4 pt-2 bg-white/40">
              {children}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

interface CareerWizardProps {
  initialSearch?: string;
  onClose: () => void;
}

interface PathwayData {
  career: string;
  relatedMDCProgram?: string;
  degreeLevel: string;
  associates?: {
    programs: string[];
    duration: string;
    keyCourses: string[];
    fullCourseList?: string[]; // Full course list from MDC database
    financial?: {
      tuitionPerYear?: string;
      housingPerMonth?: string;
      booksPerYear?: string;
      totalCost?: string;
    };
    careerOutcomes?: {
      entryLevel?: Array<{ title: string; salary: string }>;
      midCareer?: Array<{ title: string; salary: string }>;
    };
  };
  bachelors?: {
    universities?: string[];
    articulationAgreements?: string[] | string;
    duration?: string;
    keyCourses?: string[];
    fullCourseList?: string[]; // Full course list from MDC database
    financial?: {
      tuitionPerYear?: string;
      housingPerMonth?: string;
      booksPerYear?: string;
      totalCost?: string;
    };
    careerOutcomes?: {
      entryLevel?: Array<{ title: string; salary: string }>;
      midCareer?: Array<{ title: string; salary: string }>;
    };
  };
  masters?: {
    universities?: string[];
    duration?: string;
    required?: boolean;
  };
  professionalDegree?: {
    type: string;
    universities: string[];
    duration: string;
    required: boolean;
    description?: string;
  };
  certifications?: Array<{ name: string; required: boolean; timing: string }>;
  clubs?: Array<{ name: string }>;
  exams?: Array<{ name: string; required: boolean; timing: string }>;
  internships?: string[];
  alternativePathways?: string[];
  note?: string;
  error?: string;
  rawResponse?: string;
}

// API Gateway endpoint
const API_ENDPOINT = import.meta.env.VITE_API_ENDPOINT || 'https://btoccmzs5b.execute-api.us-east-1.amazonaws.com/prod/pathway';

// Helper function to format numbers with commas
const formatNumber = (value: string | undefined): string => {
  if (!value) return '';
  
  // If already has commas, return as is
  if (value.includes(',')) return value;
  
  // Handle ranges like "4000-6000" or "4000 - 6000"
  if (value.includes('-')) {
    const parts = value.split(/-|\s*-\s*/);
    return parts.map(part => {
      const num = parseInt(part.trim());
      return isNaN(num) ? part.trim() : num.toLocaleString();
    }).join('-');
  }
  
  // Handle single numbers
  const num = parseInt(value.trim());
  return isNaN(num) ? value : num.toLocaleString();
};


// PDF Generation Function - Simple Text Format
function generateRoadmapPDF(pathway: PathwayData) {
  const doc = new jsPDF();
  let yPos = 20;
  const pageWidth = doc.internal.pageSize.getWidth();
  const pageHeight = doc.internal.pageSize.getHeight();
  const margin = 20;
  const maxWidth = pageWidth - (margin * 2);
  
  // Helper function to add a new page if needed
  const checkPageBreak = (requiredSpace: number = 10) => {
    if (yPos + requiredSpace > pageHeight - 20) {
      doc.addPage();
      yPos = 20;
    }
  };
  
  // Helper function to add text with word wrap
  const addText = (text: string, fontSize: number, isBold: boolean = false, x: number = margin) => {
    checkPageBreak(fontSize + 5);
    doc.setFontSize(fontSize);
    doc.setFont('helvetica', isBold ? 'bold' : 'normal');
    doc.setTextColor(0, 0, 0);
    const lines = doc.splitTextToSize(text, maxWidth - (x - margin));
    doc.text(lines, x, yPos);
    yPos += (lines.length * fontSize * 0.4) + 5;
  };
  
  // Title
  addText('Career Roadmap', 24, true);
  yPos += 5;
  
  // Career title
  addText((pathway.career || 'Your Career Path'), 18, true);
  yPos += 10;
  
  // Advisor Note
  if (pathway.note) {
    addText('Career Advisor Message:', 12, true);
    addText(pathway.note, 10, false);
    yPos += 5;
  }
  
  // Associate's Degree Section
  if (pathway.associates) {
    addText('Associate\'s Degree', 14, true);
    yPos += 3;
    
    // Programs
    if (pathway.associates.programs && pathway.associates.programs.length > 0) {
      addText('Programs: ' + pathway.associates.programs.join(', '), 10, false);
      if (pathway.associates.duration) {
        addText('Duration: ' + pathway.associates.duration, 10, false);
      }
    }
    
    // Key Courses
    if (pathway.associates.keyCourses && pathway.associates.keyCourses.length > 0) {
      addText('Key Courses: ' + pathway.associates.keyCourses.join(', '), 10, false);
    }
    
    // Financial Information
    if (pathway.associates.financial) {
      const financial = pathway.associates.financial;
      const financialInfo: string[] = [];
      if (financial.tuitionPerYear) financialInfo.push(`Tuition: $${financial.tuitionPerYear}/year`);
      if (financial.housingPerMonth) financialInfo.push(`Housing: $${financial.housingPerMonth}/month`);
      if (financial.booksPerYear) financialInfo.push(`Books: $${financial.booksPerYear}/year`);
      if (financial.totalCost) financialInfo.push(`Total Cost: $${financial.totalCost}`);
      if (financialInfo.length > 0) {
        addText('Financial Information: ' + financialInfo.join(' | '), 10, false);
      }
    }
    
    // Career Outcomes
    if (pathway.associates.careerOutcomes) {
      const outcomes: string[] = [];
      if (pathway.associates.careerOutcomes.entryLevel && pathway.associates.careerOutcomes.entryLevel.length > 0) {
        outcomes.push('Entry-Level: ' + pathway.associates.careerOutcomes.entryLevel.map(job => `${job.title} ($${job.salary})`).join(', '));
      }
      if (pathway.associates.careerOutcomes.midCareer && pathway.associates.careerOutcomes.midCareer.length > 0) {
        outcomes.push('Mid-Career: ' + pathway.associates.careerOutcomes.midCareer.map(job => `${job.title} ($${job.salary})`).join(', '));
      }
      if (outcomes.length > 0) {
        addText('Career Outcomes: ' + outcomes.join(' | '), 10, false);
      }
    }
    
    yPos += 5;
  }
  
  // Bachelor's Degree Section
  if (pathway.bachelors) {
    addText('Bachelor\'s Degree', 14, true);
    yPos += 3;
    
    if (pathway.bachelors.universities && pathway.bachelors.universities.length > 0) {
      addText('Universities: ' + pathway.bachelors.universities.join(', '), 10, false);
      if (pathway.bachelors.duration) {
        addText('Duration: ' + pathway.bachelors.duration, 10, false);
      }
    }
    
    // Key Courses
    if (pathway.bachelors.keyCourses && pathway.bachelors.keyCourses.length > 0) {
      addText('Key Courses: ' + pathway.bachelors.keyCourses.join(', '), 10, false);
    }
    
    // Financial Information
    if (pathway.bachelors.financial) {
      const financial = pathway.bachelors.financial;
      const financialInfo: string[] = [];
      if (financial.tuitionPerYear) financialInfo.push(`Tuition: $${financial.tuitionPerYear}/year`);
      if (financial.housingPerMonth) financialInfo.push(`Housing: $${financial.housingPerMonth}/month`);
      if (financial.booksPerYear) financialInfo.push(`Books: $${financial.booksPerYear}/year`);
      if (financial.totalCost) financialInfo.push(`Total Cost: $${financial.totalCost}`);
      if (financialInfo.length > 0) {
        addText('Financial Information: ' + financialInfo.join(' | '), 10, false);
      }
    }
    
    // Career Outcomes
    if (pathway.bachelors.careerOutcomes) {
      const outcomes: string[] = [];
      if (pathway.bachelors.careerOutcomes.entryLevel && pathway.bachelors.careerOutcomes.entryLevel.length > 0) {
        outcomes.push('Entry-Level: ' + pathway.bachelors.careerOutcomes.entryLevel.map(job => `${job.title} ($${job.salary})`).join(', '));
      }
      if (pathway.bachelors.careerOutcomes.midCareer && pathway.bachelors.careerOutcomes.midCareer.length > 0) {
        outcomes.push('Mid-Career: ' + pathway.bachelors.careerOutcomes.midCareer.map(job => `${job.title} ($${job.salary})`).join(', '));
      }
      if (outcomes.length > 0) {
        addText('Career Outcomes: ' + outcomes.join(' | '), 10, false);
      }
    }
    
    yPos += 5;
  }
  
  // Certifications
  if (pathway.certifications && pathway.certifications.length > 0) {
    const certNames = pathway.certifications.map(cert => 
      typeof cert === 'string' ? cert : cert.name || ''
    ).filter(name => name.trim());
    if (certNames.length > 0) {
      addText('Certifications: ' + certNames.join(', '), 10, false);
      yPos += 3;
    }
  }
  
  // Exams
  if (pathway.exams && pathway.exams.length > 0) {
    const examNames = pathway.exams.map(exam => 
      typeof exam === 'string' ? exam : exam.name || ''
    ).filter(name => name.trim());
    if (examNames.length > 0) {
      addText('Required Exams: ' + examNames.join(', '), 10, false);
      yPos += 3;
    }
  }
  
  // Internships
  if (pathway.internships && pathway.internships.length > 0) {
    const internshipNames = pathway.internships.map(internship => 
      typeof internship === 'string' ? internship : internship.name || internship.title || ''
    ).filter(name => name.trim());
    if (internshipNames.length > 0) {
      addText('Internship Opportunities: ' + internshipNames.join(', '), 10, false);
    }
  }
  
  // Generate filename
  const filename = `${pathway.career?.replace(/[^a-z0-9]/gi, '_') || 'roadmap'}_roadmap.pdf`;
  doc.save(filename);
}

export function CareerWizard({ initialSearch = '', onClose }: CareerWizardProps) {
  const [step, setStep] = useState(1);
  const [career, setCareer] = useState(initialSearch);
  const [degree, setDegree] = useState('');
  const [pathway, setPathway] = useState<PathwayData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [placeholderIndex, setPlaceholderIndex] = useState(0);

  const placeholderExamples = [
    'cooking',
    'business',
    'basketball',
    'nursing',
    'video games',
    'lawyer',
    'movies',
    'engineering',
    'cartoons',
    'medicine'
  ];

  useEffect(() => {
    if (career.trim() === '') {
      const interval = setInterval(() => {
        setPlaceholderIndex((prev) => (prev + 1) % placeholderExamples.length);
      }, 2000); // Change every 2 seconds
      return () => clearInterval(interval);
    }
  }, [career, placeholderExamples.length]);

  const degrees = [
    { id: 'associate', name: "Associate's degree", duration: '2 years', color: 'from-cyan-400 to-cyan-600' },
    { id: 'bachelor', name: "Bachelor's degree", duration: '4 years', color: 'from-teal-400 to-teal-600' },
  ];

  // Normalize pathway data to handle API response inconsistencies
  const normalizePathwayData = (pathway: PathwayData): PathwayData => {
    // Safety check - ensure pathway is an object
    if (!pathway || typeof pathway !== 'object') {
      console.error('Invalid pathway data:', pathway);
      return {
        career: 'Unknown',
        degreeLevel: 'associate',
        associates: {
          programs: ['MDC Associate Program'],
          duration: '2 years',
          keyCourses: ['Core courses']
        }
      };
    }
    
    const normalized = { ...pathway };
    
    // Ensure arrays are always arrays
    if (normalized.associates) {
      if (!Array.isArray(normalized.associates.programs)) {
        normalized.associates.programs = normalized.associates.programs ? [normalized.associates.programs] : [];
      }
      if (!Array.isArray(normalized.associates.keyCourses)) {
        normalized.associates.keyCourses = normalized.associates.keyCourses ? [normalized.associates.keyCourses] : [];
      }
    }
    
    if (normalized.bachelors) {
      if (!Array.isArray(normalized.bachelors.universities)) {
        normalized.bachelors.universities = normalized.bachelors.universities ? [normalized.bachelors.universities] : [];
      }
      if (normalized.bachelors.articulationAgreements && !Array.isArray(normalized.bachelors.articulationAgreements)) {
        // Keep as string if it's a string, frontend will handle it
      }
      if (!Array.isArray(normalized.bachelors.keyCourses)) {
        normalized.bachelors.keyCourses = normalized.bachelors.keyCourses ? [normalized.bachelors.keyCourses] : [];
      }
    }
    
    if (normalized.masters) {
      if (!Array.isArray(normalized.masters.universities)) {
        normalized.masters.universities = normalized.masters.universities ? [normalized.masters.universities] : [];
      }
    }
    
    if (normalized.professionalDegree) {
      if (!Array.isArray(normalized.professionalDegree.universities)) {
        normalized.professionalDegree.universities = normalized.professionalDegree.universities ? [normalized.professionalDegree.universities] : [];
      }
    }
    
    // Only normalize certifications if they exist - don't add empty arrays
    if (normalized.certifications !== undefined) {
      if (!Array.isArray(normalized.certifications)) {
        normalized.certifications = normalized.certifications ? [normalized.certifications] : [];
      }
      // Remove if empty
      if (Array.isArray(normalized.certifications) && normalized.certifications.length === 0) {
        delete normalized.certifications;
      }
    }
    
    // Only normalize exams if they exist - don't add empty arrays
    if (normalized.exams !== undefined) {
      if (!Array.isArray(normalized.exams)) {
        normalized.exams = normalized.exams ? [normalized.exams] : [];
      }
      // Remove if empty
      if (Array.isArray(normalized.exams) && normalized.exams.length === 0) {
        delete normalized.exams;
      }
    }
    
    if (!Array.isArray(normalized.internships)) {
      normalized.internships = normalized.internships ? [normalized.internships] : [];
    }
    
    if (!Array.isArray(normalized.alternativePathways)) {
      normalized.alternativePathways = normalized.alternativePathways ? [normalized.alternativePathways] : [];
    }
    
    return normalized;
  };

  const roadmapSteps = [
    {
      year: 'Year 1-2',
      title: 'Foundation Building',
      description: 'Core coursework and fundamental skills',
      courses: ['Introduction to Computer Science', 'Data Structures', 'Web Development Basics'],
    },
    {
      year: 'Year 3-4',
      title: 'Specialization',
      description: 'Advanced topics and practical experience',
      courses: ['Advanced Algorithms', 'Cloud Computing (AWS)', 'Software Engineering'],
    },
    {
      year: 'Post-Graduation',
      title: 'Career Launch',
      description: 'Entry-level positions and growth',
      courses: ['AWS Solutions Architect', 'DevOps Engineer', 'Cloud Consultant'],
    },
  ];

  const fetchPathway = async () => {
    if (!career.trim() || !degree) return;

    setLoading(true);
    setError(null);

    try {
      const response = await fetch(API_ENDPOINT, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          career: career.trim(),
          degreeLevel: degree,
        }),
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.statusText}`);
      }

      let data;
      try {
        data = await response.json();
      } catch (jsonError) {
        console.error('JSON parse error:', jsonError);
        const text = await response.text();
        console.error('Response text:', text);
        throw new Error('Invalid JSON response from server');
      }

      console.log('API Response:', data); // Debug log

      // Check for error in response
      if (data.error) {
        throw new Error(data.error);
      }

      if (data.pathway) {
        try {
          // Ensure pathway is an object before normalizing
          if (!data.pathway || typeof data.pathway !== 'object') {
            throw new Error('Invalid pathway data structure');
          }
          
          // Normalize the pathway data to handle API inconsistencies
          const normalizedPathway = normalizePathwayData(data.pathway);
          
          // Ensure associates always exists - critical for rendering
          if (!normalizedPathway.associates || typeof normalizedPathway.associates !== 'object') {
            normalizedPathway.associates = {
              programs: ['MDC Associate Program'],
              duration: '2 years',
              keyCourses: ['Core courses']
            };
          }

          // Ensure financial and careerOutcomes fields exist
          if (normalizedPathway.associates) {
            if (!normalizedPathway.associates.financial) {
              normalizedPathway.associates.financial = {
                tuitionPerYear: '4000-6000',
                housingPerMonth: '800-1200',
                booksPerYear: '1200',
                totalCost: '12000-18000'
              };
            }
            if (!normalizedPathway.associates.careerOutcomes) {
              normalizedPathway.associates.careerOutcomes = {
                entryLevel: [{ title: 'Entry-Level Position', salary: '35000-45000' }],
                midCareer: [{ title: 'Mid-Career Position', salary: '50000-70000' }]
              };
            }
          }

          if (normalizedPathway.bachelors) {
            if (!normalizedPathway.bachelors.financial) {
              normalizedPathway.bachelors.financial = {
                tuitionPerYear: '8000-25000',
                housingPerMonth: '1000-1500',
                booksPerYear: '1500',
                totalCost: '21000-35000'
              };
            }
            if (!normalizedPathway.bachelors.careerOutcomes) {
              normalizedPathway.bachelors.careerOutcomes = {
                entryLevel: [{ title: 'Entry-Level Position', salary: '55000-70000' }],
                midCareer: [{ title: 'Mid-Career Position', salary: '75000-110000' }]
              };
            }
          }

          // Only add arrays if they don't exist - don't add empty arrays for certifications/exams
          // If they're missing, that means they weren't needed (which is correct)
          if (!normalizedPathway.certifications) {
            // Don't add empty array - let it be undefined so the section doesn't show
          } else if (Array.isArray(normalizedPathway.certifications) && normalizedPathway.certifications.length === 0) {
            // Remove empty certifications array
            delete normalizedPathway.certifications;
          }
          
          if (!normalizedPathway.exams) {
            // Don't add empty array - let it be undefined so the section doesn't show
          } else if (Array.isArray(normalizedPathway.exams) && normalizedPathway.exams.length === 0) {
            // Remove empty exams array
            delete normalizedPathway.exams;
          }
          
          if (!normalizedPathway.internships) normalizedPathway.internships = [];
          if (!normalizedPathway.alternativePathways) normalizedPathway.alternativePathways = [];

          // Final safety check - ensure associates exists before setting
          if (!normalizedPathway.associates || typeof normalizedPathway.associates !== 'object') {
            console.error('Associates missing after normalization, using fallback');
            normalizedPathway.associates = {
              programs: ['MDC Associate Program'],
              duration: '2 years',
              keyCourses: ['Core courses'],
              financial: {
                tuitionPerYear: '4000-6000',
                housingPerMonth: '800-1200',
                booksPerYear: '1200',
                totalCost: '12000-18000'
              },
              careerOutcomes: {
                entryLevel: [{ title: 'Entry-Level Position', salary: '35000-45000' }],
                midCareer: [{ title: 'Mid-Career Position', salary: '50000-70000' }]
              }
            };
          }
          
          setPathway(normalizedPathway);
        } catch (normalizeError) {
          console.error('Error normalizing pathway:', normalizeError);
          console.error('Raw pathway data:', data.pathway);
          // Use fallback pathway
          setPathway({
            career: career,
            degreeLevel: degree,
            associates: {
              programs: ['MDC Associate Program'],
              duration: '2 years',
              keyCourses: ['Core courses'],
              financial: {
                tuitionPerYear: '4000-6000',
                housingPerMonth: '800-1200',
                booksPerYear: '1200',
                totalCost: '12000-18000'
              },
              careerOutcomes: {
                entryLevel: [{ title: 'Entry-Level Position', salary: '35000-45000' }],
                midCareer: [{ title: 'Mid-Career Position', salary: '50000-70000' }]
              }
            },
            bachelors: degree === 'bachelor' ? {
              universities: ['Transfer to 4-year university'],
              duration: '2 years (after AA)',
              keyCourses: ['Advanced courses'],
              financial: {
                tuitionPerYear: '8000-25000',
                housingPerMonth: '1000-1500',
                booksPerYear: '1500',
                totalCost: '21000-35000'
              },
              careerOutcomes: {
                entryLevel: [{ title: 'Entry-Level Position', salary: '55000-70000' }],
                midCareer: [{ title: 'Mid-Career Position', salary: '75000-110000' }]
              }
            } : undefined,
            certifications: [],
            exams: [],
            internships: [],
            alternativePathways: []
          });
        }
      } else {
        console.error('No pathway in response:', data);
        setError('Pathway data not found in response');
        // Still set a fallback pathway to prevent white screen
        setPathway({
          career: career,
          degreeLevel: degree,
          associates: {
            programs: ['MDC Associate Program'],
            duration: '2 years',
            keyCourses: ['Core courses'],
            financial: {
              tuitionPerYear: '4000-6000',
              housingPerMonth: '800-1200',
              booksPerYear: '1200',
              totalCost: '12000-18000'
            },
            careerOutcomes: {
              entryLevel: [{ title: 'Entry-Level Position', salary: '35000-45000' }],
              midCareer: [{ title: 'Mid-Career Position', salary: '50000-70000' }]
            }
          },
          bachelors: degree === 'bachelor' ? {
            universities: ['Transfer to 4-year university'],
            duration: '2 years (after AA)',
            keyCourses: ['Advanced courses'],
            financial: {
              tuitionPerYear: '8000-25000',
              housingPerMonth: '1000-1500',
              booksPerYear: '1500',
              totalCost: '21000-35000'
            },
            careerOutcomes: {
              entryLevel: [{ title: 'Entry-Level Position', salary: '55000-70000' }],
              midCareer: [{ title: 'Mid-Career Position', salary: '75000-110000' }]
            }
          } : undefined,
          certifications: [],
          exams: [],
          internships: [],
          alternativePathways: []
        });
      }
      setStep(3);
    } catch (err) {
      console.error('Error fetching pathway:', err);
      const errorMessage = err instanceof Error ? err.message : 'Failed to generate pathway. Please try again.';
      setError(errorMessage);
      // Set a minimal fallback pathway to prevent white screen
      setPathway({
        career: career,
        degreeLevel: degree,
        associates: {
          programs: ['MDC Associate Program'],
          duration: '2 years',
          keyCourses: ['Core courses'],
          financial: {
            tuitionPerYear: '4000-6000',
            housingPerMonth: '800-1200',
            booksPerYear: '1200',
            totalCost: '12000-18000'
          },
          careerOutcomes: {
            entryLevel: [{ title: 'Entry-Level Position', salary: '35000-45000' }],
            midCareer: [{ title: 'Mid-Career Position', salary: '50000-70000' }]
          }
        },
        bachelors: degree === 'bachelor' ? {
          universities: ['Transfer to 4-year university'],
          duration: '2 years (after AA)',
          keyCourses: ['Advanced courses'],
          financial: {
            tuitionPerYear: '8000-25000',
            housingPerMonth: '1000-1500',
            booksPerYear: '1500',
            totalCost: '21000-35000'
          },
          careerOutcomes: {
            entryLevel: [{ title: 'Entry-Level Position', salary: '55000-70000' }],
            midCareer: [{ title: 'Mid-Career Position', salary: '75000-110000' }]
          }
        } : undefined,
        certifications: [],
        exams: [],
        internships: [],
        alternativePathways: []
      });
      setStep(3);
    } finally {
      setLoading(false);
    }
  };

  const handleNext = () => {
    if (step === 2 && degree) {
      // Fetch pathway when moving from step 2 to step 3
      fetchPathway();
    } else if (step < 3) {
      setStep(step + 1);
    }
  };

  const handleBack = () => {
    if (step > 1) {
      setStep(step - 1);
    } else {
      onClose();
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 z-50"
    >
      {/* Solid Backdrop */}
      <div className="absolute inset-0 bg-gradient-to-b from-cyan-50 via-white to-orange-50"></div>
      
      {/* Scrollable Content */}
      <div className="relative h-full overflow-y-auto">
      {/* Header */}
      <div className="sticky top-0 bg-white/80 backdrop-blur-md border-b border-gray-200 z-10">
        <div className="max-w-4xl mx-auto px-6 py-4 flex items-center justify-between">
          <button
            onClick={handleBack}
            className="flex items-center gap-2 text-gray-600 hover:text-cyan-600 transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
            <span>{step === 1 ? 'Cancel' : 'Back'}</span>
          </button>

          <button
            onClick={() => {
              onClose();
              window.scrollTo({ top: 0, behavior: 'smooth' });
            }}
            className="flex items-center gap-2 hover:opacity-80 transition-opacity cursor-pointer"
          >
            <Waves className="w-5 h-5 text-cyan-600" />
            <span className="text-xl font-semibold text-transparent bg-clip-text bg-gradient-to-r from-cyan-600 to-teal-600">
              Next Wave
            </span>
          </button>

          <div className="w-20"></div>
        </div>

        {/* Progress Bar */}
        <div className="max-w-4xl mx-auto px-6 pb-4">
          <div className="flex items-center gap-2">
            {[1, 2, 3].map((num) => (
              <div key={num} className="flex items-center flex-1">
                <div
                  className={`h-1 flex-1 rounded-full transition-all duration-500 ${
                    num <= step ? 'bg-gradient-to-r from-cyan-500 to-teal-500' : 'bg-gray-200'
                  }`}
                ></div>
              </div>
            ))}
          </div>
          <div className="flex justify-between mt-2 text-xs text-gray-500">
            <span className={step === 1 ? 'text-cyan-600 font-medium' : ''}>Choose Career</span>
            <span className={step === 2 ? 'text-cyan-600 font-medium' : ''}>Select Degree</span>
            <span className={step === 3 ? 'text-cyan-600 font-medium' : ''}>Your Roadmap</span>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-4xl mx-auto px-6 py-16">
        <AnimatePresence mode="wait">
          {/* Step 1: Choose Career */}
          {step === 1 && (
            <motion.div
              key="step1"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.3 }}
              className="max-w-2xl mx-auto"
            >
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="flex items-center gap-2 mb-8"
              >
                <Sparkles className="w-6 h-6 text-cyan-600" />
                      <h2 className="text-gray-700">What interests you?</h2>
              </motion.div>

                    <div className="relative w-full mb-8">
              <motion.input
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.1 }}
                type="text"
                value={career}
                onChange={(e) => setCareer(e.target.value)}
                        placeholder=""
                        className="w-full text-5xl font-light text-gray-800 bg-transparent border-none outline-none"
                autoFocus
              />
                      {career.trim() === '' && (
                        <AnimatePresence mode="wait">
                          <motion.span
                            key={placeholderIndex}
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 0.3, y: 0 }}
                            exit={{ opacity: 0, y: -10 }}
                            transition={{ duration: 0.3 }}
                            className="absolute left-0 top-0 text-5xl font-light text-gray-300 pointer-events-none"
                          >
                            {placeholderExamples[placeholderIndex]}
                          </motion.span>
                        </AnimatePresence>
                      )}
                    </div>

              <motion.button
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
                onClick={handleNext}
                disabled={!career.trim()}
                className="px-8 py-3 bg-gradient-to-r from-cyan-600 to-teal-600 text-white rounded-xl hover:shadow-lg transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
              >
                Next
                <ArrowRight className="w-5 h-5" />
              </motion.button>

              <motion.p
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.3 }}
                className="mt-6 text-sm text-gray-500 flex items-center gap-2"
              >
                <span className="text-gray-400">💡</span>
                Tip: Be as specific as possible for better recommendations
              </motion.p>
            </motion.div>
          )}

          {/* Step 2: Select Degree */}
          {step === 2 && (
            <motion.div
              key="step2"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.3 }}
              className="max-w-2xl mx-auto"
            >
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="flex items-center gap-2 mb-8"
              >
                <GraduationCap className="w-6 h-6 text-cyan-600" />
                <h2 className="text-gray-700">What degree are you pursuing?</h2>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.1 }}
                className="mb-8"
              >
                <div className="text-5xl font-light text-gray-800 mb-4">{career}</div>
                <div className="text-2xl text-gray-400 font-light">Select your degree level</div>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
                className="space-y-3 mb-8"
              >
                {degrees.map((deg, index) => (
                  <motion.button
                    key={deg.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.3 + index * 0.1 }}
                    onClick={() => setDegree(deg.id)}
                    className={`w-full p-6 rounded-2xl border-2 transition-all duration-300 text-left ${
                      degree === deg.id
                        ? 'border-cyan-500 bg-cyan-50/50 shadow-lg'
                        : 'border-gray-200 hover:border-cyan-300 bg-white/60'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <div className="font-medium text-gray-900 mb-1">{deg.name}</div>
                        <div className="text-sm text-gray-500">{deg.duration}</div>
                      </div>
                      {degree === deg.id && (
                        <CheckCircle2 className="w-6 h-6 text-cyan-600" />
                      )}
                    </div>
                  </motion.button>
                ))}
              </motion.div>

              <motion.button
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.7 }}
                onClick={handleNext}
                disabled={!degree || loading}
                className="px-8 py-3 bg-gradient-to-r from-cyan-600 to-teal-600 text-white rounded-xl hover:shadow-lg transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
              >
                      {loading ? (
                        <>
                          <motion.div
                            animate={{
                              y: [0, -4, 0],
                              scale: [1, 1.1, 1],
                            }}
                            transition={{
                              duration: 1.5,
                              repeat: Infinity,
                              ease: "easeInOut",
                            }}
                            className="w-5 h-5"
                          >
                            <Waves className="w-5 h-5" />
                          </motion.div>
                          Generating Roadmap...
                        </>
                      ) : (
                        <>
                See My Roadmap
                <ArrowRight className="w-5 h-5" />
                        </>
                      )}
              </motion.button>
            </motion.div>
          )}

          {/* Step 3: Roadmap */}
          {step === 3 && (
            <motion.div
              key="step3"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.3 }}
              className="max-w-3xl mx-auto"
            >
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="text-center mb-12"
              >
                <div className="inline-flex items-center gap-2 px-4 py-2 bg-white/60 backdrop-blur-sm border border-cyan-200/50 rounded-full mb-6 shadow-sm">
                  <CheckCircle2 className="w-4 h-4 text-cyan-600" />
                  <span className="text-cyan-900">Your Personalized Roadmap</span>
                </div>
                
                <h1 className="text-5xl font-light text-gray-800 mb-2">{career}</h1>
                      {pathway?.relatedMDCProgram && pathway.relatedMDCProgram !== career && (
                        <div className="mb-3">
                          <span className="text-lg font-medium text-cyan-600">{pathway.relatedMDCProgram}</span>
                          <span className="text-lg font-medium text-transparent bg-clip-text bg-gradient-to-r from-cyan-600 to-teal-600"> program at MDC</span>
                        </div>
                      )}
                <p className="text-xl text-gray-500">
                  {degrees.find((d) => d.id === degree)?.name}
                </p>
              </motion.div>

              {/* Error Message */}
              {error && (
                <motion.div
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="mb-8 p-4 bg-red-50 border border-red-200 rounded-xl text-red-700"
                >
                  <p className="font-medium mb-2">⚠️ Error:</p>
                  <p>{error}</p>
                </motion.div>
              )}

              {/* Show Gemini Response Debug Info */}
              {pathway && pathway.error && (
                <motion.div
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="mb-8 p-4 bg-yellow-50 border border-yellow-200 rounded-xl"
                >
                  <p className="font-medium text-yellow-800 mb-2">🔧 Gemini API Issue:</p>
                  <p className="text-sm text-yellow-700 font-mono bg-yellow-100 p-2 rounded mb-2 break-words">{pathway.error}</p>
                  <p className="text-xs text-yellow-600">Using fallback pathway data. Check Lambda logs for details.</p>
                </motion.div>
              )}

              {/* Show Gemini Response Info (if available) */}
              {pathway && pathway.rawResponse && (
                <motion.div
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="mb-8 p-7 bg-gradient-to-br from-cyan-50/80 via-teal-50/60 to-white border border-cyan-200/50 rounded-2xl shadow-sm backdrop-blur-sm"
                >
                  <div className="flex items-center gap-3 mb-5">
                    <div className="w-2.5 h-2.5 bg-cyan-500 rounded-full animate-pulse"></div>
                    <h3 className="text-lg font-semibold text-transparent bg-clip-text bg-gradient-to-r from-cyan-700 to-teal-700">
                      AI-Generated Pathway
                    </h3>
                    <div className="flex-1"></div>
                    {(() => {
                      try {
                        const rawData = typeof pathway.rawResponse === 'string' 
                          ? JSON.parse(pathway.rawResponse) 
                          : pathway.rawResponse;
                        const modelVersion = rawData?.modelVersion || 'gemini-2.5-flash';
                        return (
                          <span className="text-xs px-3 py-1.5 bg-gradient-to-r from-cyan-100 to-teal-100 text-cyan-800 rounded-full font-medium border border-cyan-200/50">
                            {modelVersion}
                          </span>
                        );
                      } catch (e) {
                        return null;
                      }
                    })()}
                  </div>
                  
                  {(() => {
                    try {
                      const rawData = typeof pathway.rawResponse === 'string' 
                        ? JSON.parse(pathway.rawResponse) 
                        : pathway.rawResponse;
                      
                      return (
                        <div className="space-y-4">
                          {/* Career Advisor Chat */}
                          {pathway.note && (
                            <div className="mt-6">
                              <h4 className="text-xs font-semibold text-cyan-700 mb-2 tracking-wide uppercase opacity-80">
                                Career Advisor Chat
                              </h4>
                              <div className="bg-transparent">
                                <p className="text-sm text-gray-700 leading-relaxed font-normal" style={{ lineHeight: '1.7', margin: 0 }}>
                                  {pathway.note}
                                </p>
                              </div>
                            </div>
                          )}
                        </div>
                      );
                    } catch (e) {
                      return (
                        <div className="text-sm text-cyan-700">
                          <p className="font-medium mb-1">✅ Response Generated Successfully</p>
                          <p className="text-xs text-cyan-600">Pathway data has been processed and displayed above.</p>
                        </div>
                      );
                    }
                  })()}
                </motion.div>
              )}

              {/* Loading State */}
              {loading && (
                <motion.div
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.9 }}
                  className="flex flex-col items-center justify-center py-20"
                >
                  <div className="mb-6">
                    <LoadingShark />
                  </div>
                  <motion.p
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.3 }}
                    className="text-lg font-medium text-gray-700 mb-2"
                  >
                    Generating your personalized pathway...
                  </motion.p>
                  <motion.p
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.5 }}
                    className="text-sm text-gray-500"
                  >
                    Our AI advisor is crafting your roadmap
                  </motion.p>
                </motion.div>
              )}

              {/* Roadmap Timeline */}
              {!loading && (
              <div className="relative mt-8">
                {/* Timeline Line */}
                <div className="absolute left-8 top-0 bottom-0 w-px bg-gradient-to-b from-cyan-200 via-teal-200 to-orange-200"></div>

                {/* Timeline Steps */}
                <div className="space-y-12">
                    {/* Show message if pathway exists but is empty - with fallback */}
                    {pathway && !pathway.associates && !pathway.bachelors && (
                      <motion.div
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="text-center py-8 text-gray-500"
                      >
                        <p>Pathway data is being processed. Please try again in a moment.</p>
                        <button
                          onClick={() => {
                            setPathway({
                              career: career,
                              degreeLevel: degree,
                              associates: {
                                programs: ['MDC Associate Program'],
                                duration: '2 years',
                                keyCourses: ['Core courses'],
                                financial: {
                                  tuitionPerYear: '4000-6000',
                                  housingPerMonth: '800-1200',
                                  booksPerYear: '1200',
                                  totalCost: '12000-18000'
                                },
                                careerOutcomes: {
                                  entryLevel: [{ title: 'Entry-Level Position', salary: '35000-45000' }],
                                  midCareer: [{ title: 'Mid-Career Position', salary: '50000-70000' }]
                                }
                              },
                              bachelors: degree === 'bachelor' ? {
                                universities: ['Transfer to 4-year university'],
                                duration: '2 years (after AA)',
                                keyCourses: ['Advanced courses'],
                                financial: {
                                  tuitionPerYear: '8000-25000',
                                  housingPerMonth: '1000-1500',
                                  booksPerYear: '1500',
                                  totalCost: '21000-35000'
                                },
                                careerOutcomes: {
                                  entryLevel: [{ title: 'Entry-Level Position', salary: '55000-70000' }],
                                  midCareer: [{ title: 'Mid-Career Position', salary: '75000-110000' }]
                                }
                              } : undefined,
                              note: `Starting with an Associate's degree at MDC provides a solid foundation for your ${career} career.`
                            });
                          }}
                          className="mt-4 px-4 py-2 bg-cyan-600 text-white rounded-lg hover:bg-cyan-700 transition-colors"
                        >
                          Show Fallback Pathway
                        </button>
                      </motion.div>
                    )}
                    {/* Associate's Degree */}
                    {pathway?.associates && (
                      <motion.div
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.2 }}
                        className="relative pl-20"
                      >
                        <div className="absolute left-0 w-16 h-16 rounded-full bg-gradient-to-br from-cyan-400 to-cyan-600 shadow-lg flex items-center justify-center">
                          <span className="text-white font-bold text-sm">AA</span>
                        </div>
                        <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 border border-gray-200/50 shadow-lg">
                          <div className="text-sm font-medium text-cyan-600 mb-2">{pathway.associates.duration}</div>
                          <h3 className="text-2xl font-semibold text-gray-900 mb-2">Associate's Degree</h3>
                          <p className="text-gray-600 mb-4">MDC Programs and Foundation Courses</p>
                          <div className="space-y-2 mb-4">
                            {pathway.associates.programs.map((program, idx) => (
                              <div key={idx} className="flex items-center gap-2 text-sm text-gray-700 leading-relaxed">
                                <div className="w-1.5 h-1.5 rounded-full bg-cyan-500 flex-shrink-0"></div>
                                <span>{program}</span>
                              </div>
                            ))}
                          </div>
                          {pathway.associates.keyCourses && pathway.associates.keyCourses.length > 0 && (
                            <Accordion 
                              title="Key Courses" 
                              icon={<GraduationCap className="w-4 h-4" />}
                              color="cyan"
                            >
                              <div className="flex flex-wrap gap-2">
                                {pathway.associates.keyCourses.slice(0, 5).map((course, idx) => (
                                  <span key={idx} className="px-3 py-1.5 bg-cyan-50 text-cyan-700 rounded-md text-xs font-medium">
                                    {course}
                                  </span>
                                ))}
                              </div>
                            </Accordion>
                          )}
                          
                          {/* Financial Data Accordion */}
                          {pathway.associates && (
                            <Accordion 
                              title="Financial Information" 
                              icon={<DollarSign className="w-4 h-4" />}
                              color="cyan"
                            >
                              <div className="space-y-3 text-sm">
                                <div className="grid grid-cols-2 gap-3">
                                  <div className="bg-white/60 rounded-lg p-3">
                                    <p className="text-xs text-gray-500 mb-1">Tuition (per year)</p>
                                    <p className="font-semibold text-gray-900">${formatNumber(pathway.associates.financial?.tuitionPerYear) || '4,000-6,000'}</p>
                                  </div>
                                  <div className="bg-white/60 rounded-lg p-3">
                                    <p className="text-xs text-gray-500 mb-1">Housing (per month)</p>
                                    <p className="font-semibold text-gray-900">${formatNumber(pathway.associates.financial?.housingPerMonth) || '800-1,200'}</p>
                                  </div>
                                  <div className="bg-white/60 rounded-lg p-3">
                                    <p className="text-xs text-gray-500 mb-1">Books & Supplies</p>
                                    <p className="font-semibold text-gray-900">${formatNumber(pathway.associates.financial?.booksPerYear) || '1,200'}/year</p>
                                  </div>
                                  <div className="bg-white/60 rounded-lg p-3">
                                    <p className="text-xs text-gray-500 mb-1">Total (2 years)</p>
                                    <p className="font-semibold text-gray-900">${formatNumber(pathway.associates.financial?.totalCost) || '12,000-18,000'}</p>
                                  </div>
                                </div>
                                <div className="bg-gradient-to-r from-cyan-50 to-teal-50 rounded-lg p-3 border border-cyan-200">
                                  <p className="text-xs font-semibold text-gray-700 mb-1">Financial Aid Available</p>
                                  <p className="text-xs text-gray-600">Pell Grants, Scholarships, Work-Study programs</p>
                                </div>
                              </div>
                            </Accordion>
                          )}

                          {/* Career Outcomes Accordion */}
                          {pathway.associates && (
                            <Accordion 
                              title="Career Outcomes & Salaries" 
                              icon={<Briefcase className="w-4 h-4" />}
                              color="cyan"
                            >
                              <div className="space-y-3 text-sm">
                                {pathway.associates.careerOutcomes.entryLevel && pathway.associates.careerOutcomes.entryLevel.length > 0 && (
                                  <div className="bg-white/60 rounded-lg p-3">
                                    <p className="font-semibold text-gray-900 mb-2">Entry-Level Positions</p>
                                    <div className="space-y-2">
                                      {pathway.associates.careerOutcomes.entryLevel.map((job, idx) => (
                                        <div key={idx} className="flex justify-between items-center">
                                          <span className="text-gray-700">{job.title}</span>
                                          <span className="font-semibold text-cyan-600">${formatNumber(job.salary)}</span>
                                        </div>
                                      ))}
                                    </div>
                                  </div>
                                )}
                                {pathway.associates.careerOutcomes.midCareer && pathway.associates.careerOutcomes.midCareer.length > 0 && (
                                  <div className="bg-white/60 rounded-lg p-3">
                                    <p className="font-semibold text-gray-900 mb-2">Mid-Career (5+ years)</p>
                                    <div className="space-y-2">
                                      {pathway.associates.careerOutcomes.midCareer.map((job, idx) => (
                                        <div key={idx} className="flex justify-between items-center">
                                          <span className="text-gray-700">{job.title}</span>
                                          <span className="font-semibold text-cyan-600">${formatNumber(job.salary)}</span>
                                        </div>
                                      ))}
                                    </div>
                                  </div>
                                )}
                                <div className="bg-gradient-to-r from-cyan-50 to-teal-50 rounded-lg p-3 border border-cyan-200">
                                  <div className="flex items-center gap-2 mb-2">
                                    <TrendingUp className="w-4 h-4 text-cyan-600" />
                                    <p className="font-semibold text-gray-900">Career Growth Potential</p>
                                  </div>
                                  <p className="text-xs text-gray-600">With additional education or certifications, salary can increase significantly</p>
                                </div>
                              </div>
                            </Accordion>
                          )}

                        </div>
                      </motion.div>
                    )}

                    {/* Bachelor's Degree */}
                    {pathway?.bachelors && (
                      <motion.div
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.4 }}
                        className="relative pl-20"
                      >
                        <div className="absolute left-0 w-16 h-16 rounded-full bg-gradient-to-br from-teal-400 to-teal-600 shadow-lg flex items-center justify-center">
                          <span className="text-white font-bold text-sm">BS</span>
                        </div>
                        <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 border border-gray-200/50 shadow-lg">
                          <div className="text-sm font-medium text-teal-600 mb-2">{pathway.bachelors.duration}</div>
                          <h3 className="text-2xl font-semibold text-gray-900 mb-2">Bachelor's Degree</h3>
                          <p className="text-gray-600 mb-4">Transfer Universities and Programs</p>
                          {pathway.bachelors.universities && pathway.bachelors.universities.length > 0 && (
                            <div className="space-y-2 mb-4">
                              {pathway.bachelors.universities.map((university, idx) => (
                                <div key={idx} className="flex items-start gap-2 text-sm text-gray-700 leading-relaxed">
                                  <div className="w-1.5 h-1.5 rounded-full bg-teal-500 mt-1.5 flex-shrink-0"></div>
                                  <span>{university}</span>
                                </div>
                              ))}
                            </div>
                          )}
                          {pathway.bachelors.articulationAgreements && (
                            <div className="mt-4 pt-4 border-t border-gray-200">
                              <p className="text-sm font-semibold text-gray-900 mb-3">Articulation Agreements:</p>
                              {Array.isArray(pathway.bachelors.articulationAgreements) ? (
                                pathway.bachelors.articulationAgreements.map((agreement, idx) => (
                                  <p key={idx} className="text-sm text-gray-700 leading-relaxed mb-2">{agreement}</p>
                                ))
                              ) : (
                                <p className="text-sm text-gray-700 leading-relaxed mb-2">{pathway.bachelors.articulationAgreements}</p>
                              )}
                            </div>
                          )}
                          {pathway.bachelors.keyCourses && pathway.bachelors.keyCourses.length > 0 && (
                            <Accordion 
                              title="Key Courses" 
                              icon={<GraduationCap className="w-4 h-4" />}
                              color="teal"
                            >
                              <div className="flex flex-wrap gap-2">
                                {pathway.bachelors.keyCourses.slice(0, 5).map((course, idx) => (
                                  <span key={idx} className="px-3 py-1.5 bg-teal-50 text-teal-700 rounded-md text-xs font-medium">
                                    {course}
                                  </span>
                                ))}
                              </div>
                            </Accordion>
                          )}

                          {/* Financial Data Accordion */}
                          {pathway.bachelors && (
                            <Accordion 
                              title="Financial Information" 
                              icon={<DollarSign className="w-4 h-4" />}
                              color="teal"
                            >
                              <div className="space-y-3 text-sm">
                                <div className="grid grid-cols-2 gap-3">
                                  <div className="bg-white/60 rounded-lg p-3">
                                    <p className="text-xs text-gray-500 mb-1">Tuition (per year)</p>
                                    <p className="font-semibold text-gray-900">${formatNumber(pathway.bachelors.financial?.tuitionPerYear) || '8,000-25,000'}</p>
                                  </div>
                                  <div className="bg-white/60 rounded-lg p-3">
                                    <p className="text-xs text-gray-500 mb-1">Housing (per month)</p>
                                    <p className="font-semibold text-gray-900">${formatNumber(pathway.bachelors.financial?.housingPerMonth) || '1,000-1,500'}</p>
                                  </div>
                                  <div className="bg-white/60 rounded-lg p-3">
                                    <p className="text-xs text-gray-500 mb-1">Books & Supplies</p>
                                    <p className="font-semibold text-gray-900">${formatNumber(pathway.bachelors.financial?.booksPerYear) || '1,500'}/year</p>
                                  </div>
                                  <div className="bg-white/60 rounded-lg p-3">
                                    <p className="text-xs text-gray-500 mb-1">Total (2 years)</p>
                                    <p className="font-semibold text-gray-900">${formatNumber(pathway.bachelors.financial?.totalCost) || '21,000-35,000'}</p>
                                  </div>
                                </div>
                                <div className="bg-gradient-to-r from-teal-50 to-cyan-50 rounded-lg p-3 border border-teal-200">
                                  <p className="text-xs font-semibold text-gray-700 mb-1">Financial Aid Available</p>
                                  <p className="text-xs text-gray-600">Federal loans, scholarships, grants, work-study programs</p>
                                </div>
                              </div>
                            </Accordion>
                          )}

                          {/* Career Outcomes Accordion */}
                          {pathway.bachelors && (
                            <Accordion 
                              title="Career Outcomes & Salaries" 
                              icon={<Briefcase className="w-4 h-4" />}
                              color="teal"
                            >
                              <div className="space-y-3 text-sm">
                                {pathway.bachelors.careerOutcomes.entryLevel && pathway.bachelors.careerOutcomes.entryLevel.length > 0 && (
                                  <div className="bg-white/60 rounded-lg p-3">
                                    <p className="font-semibold text-gray-900 mb-2">Entry-Level Positions</p>
                                    <div className="space-y-2">
                                      {pathway.bachelors.careerOutcomes.entryLevel.map((job, idx) => (
                                        <div key={idx} className="flex justify-between items-center">
                                          <span className="text-gray-700">{job.title}</span>
                                          <span className="font-semibold text-teal-600">${formatNumber(job.salary)}</span>
                                        </div>
                                      ))}
                                    </div>
                                  </div>
                                )}
                                {pathway.bachelors.careerOutcomes.midCareer && pathway.bachelors.careerOutcomes.midCareer.length > 0 && (
                                  <div className="bg-white/60 rounded-lg p-3">
                                    <p className="font-semibold text-gray-900 mb-2">Mid-Career (5+ years)</p>
                                    <div className="space-y-2">
                                      {pathway.bachelors.careerOutcomes.midCareer.map((job, idx) => (
                                        <div key={idx} className="flex justify-between items-center">
                                          <span className="text-gray-700">{job.title}</span>
                                          <span className="font-semibold text-teal-600">${formatNumber(job.salary)}</span>
                                        </div>
                                      ))}
                                    </div>
                                  </div>
                                )}
                                <div className="bg-gradient-to-r from-teal-50 to-cyan-50 rounded-lg p-3 border border-teal-200">
                                  <div className="flex items-center gap-2 mb-2">
                                    <TrendingUp className="w-4 h-4 text-teal-600" />
                                    <p className="font-semibold text-gray-900">Career Growth Potential</p>
                                  </div>
                                  <p className="text-xs text-gray-600">With experience and advanced degrees, salary can reach $120K+</p>
                                </div>
                              </div>
                            </Accordion>
                          )}

                        </div>
                      </motion.div>
                    )}

                    {/* Master's Degree */}
                    {pathway?.masters && pathway.masters.required && (
                      <motion.div
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.6 }}
                        className="relative pl-20"
                      >
                        <div className="absolute left-0 w-16 h-16 rounded-full bg-gradient-to-br from-orange-400 to-orange-600 shadow-lg flex items-center justify-center">
                          <span className="text-white font-bold text-sm">MS</span>
                        </div>
                        <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 border border-gray-200/50 shadow-lg">
                          <div className="text-sm font-medium text-orange-600 mb-2">{pathway.masters.duration}</div>
                          <h3 className="text-2xl font-semibold text-gray-900 mb-2">Master's Degree</h3>
                          {pathway.masters.universities && pathway.masters.universities.length > 0 && (
                            <div className="space-y-2">
                              {pathway.masters.universities.map((university, idx) => (
                                <div key={idx} className="flex items-start gap-2 text-sm text-gray-700 leading-relaxed">
                                  <div className="w-1.5 h-1.5 rounded-full bg-orange-500 mt-1.5 flex-shrink-0"></div>
                                  <span>{university}</span>
                                </div>
                              ))}
                            </div>
                          )}
                        </div>
                      </motion.div>
                    )}

                    {/* Professional Degree (M.D., J.D., etc.) */}
                    {pathway?.professionalDegree && pathway.professionalDegree.required && (
                      <motion.div
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.7 }}
                        className="relative pl-20"
                      >
                        <div className="absolute left-0 w-16 h-16 rounded-full bg-gradient-to-br from-indigo-400 to-indigo-600 shadow-lg flex items-center justify-center">
                          {(() => {
                            const degreeType = pathway.professionalDegree.type?.toLowerCase() || '';
                            if (degreeType.includes('j.d') || degreeType.includes('juris') || degreeType.includes('law')) {
                              return <Scale className="w-8 h-8 text-white" />;
                            } else if (degreeType.includes('m.d') || degreeType.includes('medical') || degreeType.includes('doctor')) {
                              return <Stethoscope className="w-8 h-8 text-white" />;
                            } else {
                              return <GraduationCap className="w-8 h-8 text-white" />;
                            }
                          })()}
                        </div>
                        <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 border border-gray-200/50 shadow-lg">
                          <div className="text-sm font-medium text-indigo-600 mb-2">{pathway.professionalDegree.duration}</div>
                          <h3 className="text-2xl font-semibold text-gray-900 mb-2">Professional Degree</h3>
                          {pathway.professionalDegree.type && (
                            <p className="text-sm text-indigo-600 font-medium mb-3">{pathway.professionalDegree.type}</p>
                          )}
                          {pathway.professionalDegree.description && (
                            <p className="text-sm text-gray-600 mb-4">{pathway.professionalDegree.description}</p>
                          )}
                          {pathway.professionalDegree.universities && pathway.professionalDegree.universities.length > 0 && (
                            <div className="space-y-2">
                              {pathway.professionalDegree.universities.map((university, idx) => (
                                <div key={idx} className="flex items-start gap-2 text-sm text-gray-700 leading-relaxed">
                                  <div className="w-1.5 h-1.5 rounded-full bg-indigo-500 mt-1.5 flex-shrink-0"></div>
                                  <span>{university}</span>
                                </div>
                              ))}
                            </div>
                          )}
                        </div>
                      </motion.div>
                    )}

                    {/* Certifications & Exams - Only show if both exist and have valid content */}
                    {(() => {
                      // Helper function to check if array has valid content (not just hyphens or empty strings)
                      const hasValidContent = (arr: any[]): boolean => {
                        if (!arr || arr.length === 0) return false;
                        return arr.some(item => {
                          if (typeof item === 'string') {
                            const trimmed = item.trim();
                            return trimmed.length > 0 && trimmed !== '-';
                          }
                          if (typeof item === 'object' && item !== null) {
                            const name = item.name || item;
                            const trimmed = String(name).trim();
                            return trimmed.length > 0 && trimmed !== '-';
                          }
                          return false;
                        });
                      };

                      const hasCertifications = pathway?.certifications && 
                        Array.isArray(pathway.certifications) && 
                        hasValidContent(pathway.certifications);
                      
                      const hasExams = pathway?.exams && 
                        Array.isArray(pathway.exams) && 
                        hasValidContent(pathway.exams);

                      // Only show if at least one has valid content
                      if (!hasCertifications && !hasExams) return null;

                      return (
                        <motion.div
                          initial={{ opacity: 0, x: -20 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ delay: 0.8 }}
                          className="relative pl-20 mt-8"
                        >
                          <div className="absolute left-0 top-0 w-16 h-16 rounded-full bg-gradient-to-br from-purple-500 to-purple-700 shadow-lg flex items-center justify-center" style={{ background: 'linear-gradient(to bottom right, rgb(168, 85, 247), rgb(126, 34, 206))' }}>
                            <CheckCircle2 className="w-7 h-7 text-white fill-white" />
                          </div>
                          <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 border border-gray-200/50 shadow-lg">
                            <h3 className="text-2xl font-semibold text-gray-900 mb-4">Certifications & Exams</h3>
                            {hasCertifications && (
                              <div className="mb-4">
                                <p className="text-sm font-semibold text-gray-900 mb-3">Certifications:</p>
                                {pathway.certifications
                                  .filter(cert => {
                                    const name = typeof cert === 'string' ? cert : (cert?.name || cert);
                                    const trimmed = String(name).trim();
                                    return trimmed.length > 0 && trimmed !== '-';
                                  })
                                  .map((cert, idx) => {
                                    const certName = typeof cert === 'string' ? cert : (cert?.name || cert);
                                    const required = typeof cert === 'object' && cert?.required;
                                    // Keep it concise - just the name, no timing or extra text
                                    return (
                                      <div key={idx} className="flex items-start gap-2 text-sm text-gray-700 mb-1.5">
                                        <div className="w-1.5 h-1.5 rounded-full bg-purple-500 mt-1.5 flex-shrink-0"></div>
                                        <span className="line-clamp-1">{certName}{required && <span className="text-red-600 font-medium"> (Required)</span>}</span>
                                      </div>
                                    );
                                  })}
                              </div>
                            )}
                            {hasExams && (
                              <div>
                                <p className="text-sm font-semibold text-gray-900 mb-3">Exams:</p>
                                {pathway.exams
                                  .filter(exam => {
                                    const name = typeof exam === 'string' ? exam : (exam?.name || exam);
                                    const trimmed = String(name).trim();
                                    return trimmed.length > 0 && trimmed !== '-';
                                  })
                                  .map((exam, idx) => {
                                    const examName = typeof exam === 'string' ? exam : (exam?.name || exam);
                                    const required = typeof exam === 'object' && exam?.required;
                                    const timing = typeof exam === 'object' && exam?.timing ? ` - ${exam.timing}` : '';
                                    return (
                                      <div key={idx} className="flex items-start gap-2 text-sm text-gray-700 mb-2 leading-relaxed">
                                        <div className="w-1.5 h-1.5 rounded-full bg-purple-500 mt-1.5 flex-shrink-0"></div>
                                        <span>{examName}{required && <span className="text-red-600 font-medium"> (Required)</span>}{timing}</span>
                                      </div>
                                    );
                                  })}
                              </div>
                            )}
                          </div>
                        </motion.div>
                      );
                    })()}

                    {/* Internships */}
                    {pathway?.internships && pathway.internships.length > 0 && (
                      <motion.div
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 1.0 }}
                        className="relative pl-20"
                      >
                        <div className="absolute left-0 w-16 h-16 rounded-full bg-gradient-to-br from-emerald-400 to-emerald-600 shadow-lg flex items-center justify-center">
                          <MapPin className="w-8 h-8 text-white" />
                        </div>
                        <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 border border-gray-200/50 shadow-lg">
                          <h3 className="text-2xl font-semibold text-gray-900 mb-4">Internships & Experience</h3>
                          <div className="space-y-2">
                            {pathway.internships.map((internship, idx) => (
                              <div key={idx} className="flex items-start gap-2 text-sm text-gray-700 leading-relaxed">
                                <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 mt-1.5 flex-shrink-0"></div>
                                <span>{internship}</span>
                              </div>
                            ))}
                          </div>
                        </div>
                      </motion.div>
                    )}

                    {/* Fallback to hardcoded steps if no pathway data or pathway is empty */}
                    {(!pathway || (!pathway.associates && !pathway.bachelors)) && !loading && roadmapSteps.map((roadmapStep, index) => (
                    <motion.div
                      key={index}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 0.2 + index * 0.2 }}
                      className="relative pl-20"
                    >
                      <div className={`absolute left-0 w-16 h-16 rounded-full bg-gradient-to-br ${
                        index === 0 ? 'from-cyan-400 to-cyan-600' :
                        index === 1 ? 'from-teal-400 to-teal-600' :
                        'from-orange-400 to-orange-600'
                      } shadow-lg flex items-center justify-center`}>
                        <span className="text-white font-bold text-sm">{index + 1}</span>
                      </div>
                      <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 border border-gray-200/50 shadow-lg">
                        <div className="text-sm font-medium text-cyan-600 mb-2">{roadmapStep.year}</div>
                        <h3 className="text-2xl font-semibold text-gray-900 mb-2">{roadmapStep.title}</h3>
                        <p className="text-gray-600 mb-4">{roadmapStep.description}</p>
                        <div className="space-y-2">
                          {roadmapStep.courses.map((course, idx) => (
                            <div key={idx} className="flex items-center gap-2 text-sm text-gray-700">
                              <div className="w-1.5 h-1.5 rounded-full bg-cyan-500"></div>
                              {course}
                            </div>
                          ))}
                        </div>
                      </div>
                    </motion.div>
                  ))}
                </div>
              </div>
              )}

              {/* Action Buttons */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.8 }}
                className="mt-16 flex flex-col sm:flex-row gap-4 justify-center"
              >
                <button 
                  onClick={() => {
                    if (pathway) {
                      generateRoadmapPDF(pathway);
                    }
                  }}
                  className="px-8 py-4 bg-gradient-to-r from-cyan-600 to-teal-600 text-white rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 flex items-center justify-center gap-2"
                >
                  <Download className="w-5 h-5" />
                  Save My Roadmap
                </button>
                <button 
                  onClick={() => {
                    setStep(1);
                    setCareer('');
                    setDegree('');
                    setPathway(null);
                    setError(null);
                  }}
                  className="px-8 py-4 bg-white border-2 border-gray-300 text-gray-700 rounded-xl hover:border-cyan-300 hover:shadow-lg transition-all duration-300 flex items-center justify-center gap-2"
                >
                  <Sparkles className="w-5 h-5" />
                  New Wave
                </button>
              </motion.div>

              <motion.p
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 1 }}
                className="mt-8 text-center text-sm text-gray-500"
              >
                This roadmap is personalized based on your goals and current education level
              </motion.p>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
      </div>
    </motion.div>
  );
}
