// get the ninja-keys element
const ninja = document.querySelector('ninja-keys');

// add the home and posts menu items
ninja.data = [{
    id: "nav-about",
    title: "about",
    section: "Navigation",
    handler: () => {
      window.location.href = "/";
    },
  },{id: "nav-publications",
          title: "publications",
          description: "Journal articles in biomedical statistics, clinical data science, machine learning, and digital health.",
          section: "Navigation",
          handler: () => {
            window.location.href = "/publications/";
          },
        },{id: "nav-projects",
          title: "projects",
          description: "Selected research projects in predictive modeling, causal inference, and healthcare AI.",
          section: "Navigation",
          handler: () => {
            window.location.href = "/projects/";
          },
        },{id: "nav-teaching",
          title: "teaching",
          description: "Guest lectures and teaching assistantships in biomedical AI, machine learning, and data science.",
          section: "Navigation",
          handler: () => {
            window.location.href = "/teaching/";
          },
        },{id: "nav-cv",
          title: "CV",
          description: "Curriculum Vitae of Sungjun Hong — Healthcare Data Scientist, Postdoctoral Fellow",
          section: "Navigation",
          handler: () => {
            window.location.href = "/cv/";
          },
        },{id: "nav-people",
          title: "people",
          description: "Collaborators, mentors, and research colleagues.",
          section: "Navigation",
          handler: () => {
            window.location.href = "/people/";
          },
        },{id: "nav-blog",
          title: "blog",
          description: "",
          section: "Navigation",
          handler: () => {
            window.location.href = "/blog/";
          },
        },{id: "news-our-paper-on-the-association-between-alcohol-consumption-and-serum-uric-acid-levels-has-been-published-in-the-journal-of-korean-medical-science-jkms",
          title: 'Our paper on the association between alcohol consumption and serum uric acid levels...',
          description: "",
          section: "News",},{id: "news-our-findings-on-the-association-between-alcohol-consumption-patterns-and-serum-uric-acid-levels-were-featured-in-korea-biomedical-review",
          title: 'Our findings on the association between alcohol consumption patterns and serum uric acid...',
          description: "",
          section: "News",},{id: "news-released-sam-shared-anchor-matching-an-open-source-matching-framework-for-multigroup-observational-studies-with-implementations-in-r-and-python-sam-python-sam-r",
          title: 'Released SAM (Shared Anchor Matching), an open-source matching framework for multigroup observational studies,...',
          description: "",
          section: "News",},{id: "news-i-will-join-the-division-of-gastroenterology-amp-amp-hepatology-at-nyu-grossman-school-of-medicine-as-a-postdoctoral-fellow",
          title: 'I will join the Division of Gastroenterology &amp;amp;amp; Hepatology at NYU Grossman School...',
          description: "",
          section: "News",},{id: "projects-investigating-the-usefulness-of-histological-activity-evaluation-using-deep-learning-in-patients-with-ulcerative-colitis",
          title: 'Investigating the Usefulness of Histological Activity Evaluation using Deep Learning in Patients with...',
          description: "Segmentation + prediction pipeline for Nancy-grade histologic activity, with multi-center external validation",
          section: "Projects",handler: () => {
              window.location.href = "/projects/1_ulcerative_colitis_deep_learning/";
            },},{id: "projects-development-of-bacteremia-prediction-model-in-pediatric-cancer-patients-with-persistent-neutropenic-fever",
          title: 'Development of Bacteremia Prediction Model in Pediatric Cancer Patients with Persistent Neutropenic Fever...',
          description: "Prediction model development for bacteremia in pediatric oncology patients with persistent neutropenic fever",
          section: "Projects",handler: () => {
              window.location.href = "/projects/2_bacteremia_prediction_pediatric/";
            },},{id: "projects-converged-image-based-precision-oncology-ai-solution-for-gastrointestinal-malignancies-radiomics-feature-selection-framework",
          title: 'Converged Image-based Precision Oncology AI Solution for Gastrointestinal Malignancies (Radiomics feature selection framework)...',
          description: "Clinical prediction modeling for radio-genomics and a reusable radiomics feature selection framework",
          section: "Projects",handler: () => {
              window.location.href = "/projects/3_radiomics_feature_selection/";
            },},{id: "projects-comparison-of-machine-learning-based-propensity-score-methods-for-imbalanced-three-treatment-groups",
          title: 'Comparison of Machine Learning-Based Propensity Score Methods for Imbalanced Three Treatment Groups',
          description: "Doctoral research on non-parametric, machine learning-based propensity score methodology for causal inference",
          section: "Projects",handler: () => {
              window.location.href = "/projects/4_propensity_score_methods/";
            },},{id: "projects-development-and-implementation-of-cdm-fhir-and-ai-based-precision-medicine-platform-to-improve-national-medical-quality-and-safety-for-emergency-and-critical-patients",
          title: 'Development and Implementation of CDM, FHIR and AI-based Precision Medicine Platform to improve...',
          description: "CDM/FHIR/AI-based precision medicine platform for emergency and critical care quality and safety",
          section: "Projects",handler: () => {
              window.location.href = "/projects/5_cdm_fhir_precision_medicine/";
            },},{
        id: 'social-email',
        title: 'email',
        section: 'Socials',
        handler: () => {
          window.open("mailto:%68%73%6A%32%38%36%34@%67%6D%61%69%6C.%63%6F%6D", "_blank");
        },
      },{
        id: 'social-cv',
        title: 'CV',
        section: 'Socials',
        handler: () => {
          window.open("/assets/pdf/sungjun_hong_cv.pdf", "_blank");
        },
      },{
        id: 'social-github',
        title: 'GitHub',
        section: 'Socials',
        handler: () => {
          window.open("https://github.com/hong-sj", "_blank");
        },
      },{
        id: 'social-linkedin',
        title: 'LinkedIn',
        section: 'Socials',
        handler: () => {
          window.open("https://www.linkedin.com/in/sungjun-hong", "_blank");
        },
      },{
        id: 'social-scholar',
        title: 'Google Scholar',
        section: 'Socials',
        handler: () => {
          window.open("https://scholar.google.com/citations?user=dOZXFgoAAAAJ", "_blank");
        },
      },{
        id: 'social-orcid',
        title: 'ORCID',
        section: 'Socials',
        handler: () => {
          window.open("https://orcid.org/0000-0003-2797-238X", "_blank");
        },
      },{
        id: 'social-scopus',
        title: 'Scopus',
        section: 'Socials',
        handler: () => {
          window.open("https://www.scopus.com/authid/detail.uri?authorId=57210552646", "_blank");
        },
      },{
      id: 'light-theme',
      title: 'Change theme to light',
      description: 'Change the theme of the site to Light',
      section: 'Theme',
      handler: () => {
        setThemeSetting("light");
      },
    },
    {
      id: 'dark-theme',
      title: 'Change theme to dark',
      description: 'Change the theme of the site to Dark',
      section: 'Theme',
      handler: () => {
        setThemeSetting("dark");
      },
    },
    {
      id: 'system-theme',
      title: 'Use system default theme',
      description: 'Change the theme of the site to System Default',
      section: 'Theme',
      handler: () => {
        setThemeSetting("system");
      },
    },];
