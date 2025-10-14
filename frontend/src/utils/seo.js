// M&A SaaS Platform - Comprehensive SEO Optimization
// Optimized for Traditional Search Engines and AI Search Systems
// Platform: "100 Days and Beyond" M&A Ecosystem

/**
 * SEO Configuration for M&A SaaS Platform
 * Optimized for both traditional search engines and AI-powered search systems
 */

export const SEO_CONFIG = {
  // Primary Brand Information
  siteName: '100 Days and Beyond',
  siteUrl: 'https://100daysandbeyond.com',
  defaultTitle: '100 Days and Beyond - M&A Mastery Platform for Dealmakers',
  defaultDescription:
    'Transform your M&A expertise with our comprehensive platform. Tools, community, and insights for successful deal-making. Join thousands of professionals building wealth through strategic acquisitions.',

  // Business Focus Keywords
  primaryKeywords: [
    'M&A platform',
    'mergers and acquisitions',
    'deal sourcing',
    'business acquisition',
    'dealmaker tools',
    'M&A community',
    'acquisition strategy',
    'business valuation',
    'due diligence',
    'deal management',
  ],

  // Long-tail Keywords for AI Search
  longTailKeywords: [
    'how to buy a business with no money down',
    'M&A deal sourcing strategies',
    'business acquisition due diligence checklist',
    'small business acquisition financing',
    'M&A valuation methods and models',
    'dealmaker community and networking',
    'business acquisition success stories',
    'M&A integration best practices',
  ],

  // Structured Data Schema
  organizationSchema: {
    '@context': 'https://schema.org',
    '@type': 'Organization',
    name: '100 Days and Beyond',
    url: 'https://100daysandbeyond.com',
    logo: 'https://100daysandbeyond.com/logo.png',
    description:
      'Leading M&A platform providing tools, community, and expertise for successful business acquisitions and wealth building.',
    foundingDate: '2025',
    industry: 'Financial Services',
    serviceArea: 'Global',
    contactPoint: {
      '@type': 'ContactPoint',
      telephone: '+1-800-DEALMAKER',
      contactType: 'Customer Service',
      email: 'support@100daysandbeyond.com',
    },
    sameAs: [
      'https://linkedin.com/company/100daysandbeyond',
      'https://twitter.com/100daysandbeyond',
    ],
  },

  // Software Application Schema
  softwareSchema: {
    '@context': 'https://schema.org',
    '@type': 'SoftwareApplication',
    name: '100 Days and Beyond M&A Platform',
    applicationCategory: 'BusinessApplication',
    operatingSystem: 'Web Browser',
    offers: {
      '@type': 'Offer',
      price: '279',
      priceCurrency: 'USD',
      priceValidUntil: '2025-12-31',
    },
    aggregateRating: {
      '@type': 'AggregateRating',
      ratingValue: '4.8',
      ratingCount: '150',
    },
  },
};

/**
 * Generate page-specific SEO metadata
 */
export const generateSEOMetadata = (page) => {
  const baseMetadata = {
    title: SEO_CONFIG.defaultTitle,
    description: SEO_CONFIG.defaultDescription,
    keywords: SEO_CONFIG.primaryKeywords.join(', '),
    canonical: `${SEO_CONFIG.siteUrl}${page.path || ''}`,
    openGraph: {
      title: page.title || SEO_CONFIG.defaultTitle,
      description: page.description || SEO_CONFIG.defaultDescription,
      url: `${SEO_CONFIG.siteUrl}${page.path || ''}`,
      siteName: SEO_CONFIG.siteName,
      images: [
        {
          url: `${SEO_CONFIG.siteUrl}/og-image.jpg`,
          width: 1200,
          height: 630,
          alt: '100 Days and Beyond - M&A Mastery Platform',
        },
      ],
      type: 'website',
    },
    twitter: {
      card: 'summary_large_image',
      site: '@100daysandbeyond',
      creator: '@100daysandbeyond',
      title: page.title || SEO_CONFIG.defaultTitle,
      description: page.description || SEO_CONFIG.defaultDescription,
      image: `${SEO_CONFIG.siteUrl}/twitter-image.jpg`,
    },
  };

  // Page-specific optimizations
  const pageConfigs = {
    home: {
      title: 'M&A Platform for Dealmakers | 100 Days and Beyond',
      description:
        'Join the leading M&A platform with tools, community, and expert guidance. Start your journey to successful business acquisitions and wealth building today.',
      keywords:
        'M&A platform, business acquisition, dealmaker tools, mergers acquisitions, deal sourcing',
    },
    pricing: {
      title: 'M&A Platform Pricing - Solo, Growth & Enterprise Plans',
      description:
        'Choose the perfect M&A platform plan for your needs. From solo dealmakers to enterprise teams. Start with our 14-day free trial.',
      keywords:
        'M&A platform pricing, business acquisition tools cost, dealmaker subscription plans',
    },
    community: {
      title: 'M&A Community - Connect with Expert Dealmakers',
      description:
        'Join thousands of M&A professionals sharing insights, deals, and strategies. Network with successful dealmakers and grow your expertise.',
      keywords: 'M&A community, dealmaker network, business acquisition forum, M&A professionals',
    },
    podcast: {
      title: 'M&A Mastery Podcast - Weekly Insights for Dealmakers',
      description:
        'Weekly podcast featuring M&A experts, successful dealmakers, and actionable strategies for business acquisitions and wealth building.',
      keywords: 'M&A podcast, business acquisition podcast, dealmaker interviews, M&A strategies',
    },
    blog: {
      title: 'M&A Insights Blog - Expert Analysis and Strategies',
      description:
        'In-depth articles on M&A strategies, market analysis, deal structures, and success stories from experienced dealmakers.',
      keywords: 'M&A blog, business acquisition articles, dealmaker insights, M&A market analysis',
    },
  };

  return {
    ...baseMetadata,
    ...pageConfigs[page.type],
    ...page,
  };
};

/**
 * AI Search Optimization - Structured content for AI understanding
 */
export const AI_SEARCH_OPTIMIZATION = {
  // Question-Answer Pairs for AI Systems
  faqSchema: {
    '@context': 'https://schema.org',
    '@type': 'FAQPage',
    mainEntity: [
      {
        '@type': 'Question',
        name: 'What is 100 Days and Beyond?',
        acceptedAnswer: {
          '@type': 'Answer',
          text: '100 Days and Beyond is a comprehensive M&A platform that provides tools, community, and expert guidance for successful business acquisitions. We help dealmakers source deals, conduct due diligence, and build wealth through strategic acquisitions.',
        },
      },
      {
        '@type': 'Question',
        name: 'How much does the M&A platform cost?',
        acceptedAnswer: {
          '@type': 'Answer',
          text: 'We offer three pricing tiers: Solo Dealmaker at $279/month, Growth Firm at $798/month, and Enterprise at $1,598/month. All plans include a 14-day free trial and annual discounts.',
        },
      },
      {
        '@type': 'Question',
        name: 'What tools are included in the M&A platform?',
        acceptedAnswer: {
          '@type': 'Answer',
          text: 'Our platform includes deal sourcing tools, due diligence checklists, valuation models, document management, team collaboration features, community access, and AI-powered insights for successful M&A transactions.',
        },
      },
    ],
  },

  // Service Schema for AI Understanding
  serviceSchema: {
    '@context': 'https://schema.org',
    '@type': 'Service',
    name: 'M&A Platform and Consulting Services',
    provider: {
      '@type': 'Organization',
      name: '100 Days and Beyond',
    },
    serviceType: 'Business Acquisition Platform',
    description:
      'Comprehensive M&A platform with tools, community, and consulting services for successful business acquisitions and wealth building.',
    offers: [
      {
        '@type': 'Offer',
        name: 'Solo Dealmaker Plan',
        price: '279',
        priceCurrency: 'USD',
      },
      {
        '@type': 'Offer',
        name: 'Growth Firm Plan',
        price: '798',
        priceCurrency: 'USD',
      },
      {
        '@type': 'Offer',
        name: 'Enterprise Plan',
        price: '1598',
        priceCurrency: 'USD',
      },
    ],
  },
};

/**
 * Performance Optimization for SEO
 */
export const PERFORMANCE_CONFIG = {
  // Critical Resource Hints
  preconnectDomains: [
    'https://api.100daysandbeyond.com',
    'https://fonts.googleapis.com',
    'https://fonts.gstatic.com',
  ],

  // DNS Prefetch for External Resources
  dnsPrefetchDomains: [
    'https://www.google-analytics.com',
    'https://www.googletagmanager.com',
    'https://clerk.com',
  ],

  // Critical CSS for Above-the-Fold Content
  criticalCSS: `
    /* Critical styles for immediate rendering */
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }
    .hero-section { min-height: 60vh; display: flex; align-items: center; }
    .navigation { position: sticky; top: 0; z-index: 100; }
  `,
};

/**
 * Content Optimization for AI Search
 */
export const CONTENT_OPTIMIZATION = {
  // Semantic HTML5 Structure
  semanticStructure: {
    header: 'Site navigation and branding',
    main: 'Primary content area',
    section: 'Distinct content sections',
    article: 'Standalone content pieces',
    aside: 'Supplementary content',
    footer: 'Site information and links',
  },

  // Heading Hierarchy for Content Structure
  headingStrategy: {
    h1: 'Primary page title (one per page)',
    h2: 'Major section headings',
    h3: 'Subsection headings',
    h4: 'Detail headings',
    h5: 'Minor headings',
    h6: 'Least important headings',
  },

  // Content Guidelines for AI Understanding
  contentGuidelines: {
    clarity: 'Use clear, concise language that explains complex M&A concepts',
    expertise: 'Demonstrate deep knowledge of M&A processes and strategies',
    authority: 'Reference credible sources and real-world experience',
    trustworthiness: 'Provide transparent information about services and pricing',
    helpfulness: 'Focus on solving user problems and providing actionable insights',
  },
};

/**
 * Local SEO Configuration (if applicable)
 */
export const LOCAL_SEO = {
  businessSchema: {
    '@context': 'https://schema.org',
    '@type': 'ProfessionalService',
    name: '100 Days and Beyond',
    description: 'M&A consulting and platform services',
    url: 'https://100daysandbeyond.com',
    telephone: '+1-800-DEALMAKER',
    email: 'support@100daysandbeyond.com',
    priceRange: '$279-$1598',
    serviceArea: {
      '@type': 'Place',
      name: 'Global',
    },
  },
};

/**
 * Analytics and Tracking Configuration
 */
export const ANALYTICS_CONFIG = {
  // Google Analytics 4
  ga4: {
    measurementId: 'G-XXXXXXXXXX', // Replace with actual ID
    config: {
      page_title: document.title,
      page_location: window.location.href,
      content_group1: 'M&A Platform',
      content_group2: 'SaaS Application',
    },
  },

  // Conversion Tracking Events
  conversionEvents: [
    'sign_up',
    'subscribe',
    'trial_start',
    'consultation_request',
    'event_registration',
    'community_join',
  ],

  // Custom Dimensions for Business Intelligence
  customDimensions: {
    user_type: 'prospect|trial|subscriber|enterprise',
    subscription_tier: 'solo|growth|enterprise',
    user_journey_stage: 'awareness|consideration|decision|retention',
  },
};

/**
 * Export all SEO utilities
 */
export default {
  SEO_CONFIG,
  generateSEOMetadata,
  AI_SEARCH_OPTIMIZATION,
  PERFORMANCE_CONFIG,
  CONTENT_OPTIMIZATION,
  LOCAL_SEO,
  ANALYTICS_CONFIG,
};
