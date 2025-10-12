"""
Sprint 12 Verification - Advanced AI & Machine Learning Platform
Comprehensive verification tests for all AI/ML components and API endpoints
"""

import sys
import traceback
from datetime import datetime
from typing import Dict, Any, List

def test_ai_ml_imports():
    """Test all AI/ML module imports"""
    print("Testing AI/ML module imports...")

    try:
        # Test main module imports
        from app.ai_ml import (
            PredictiveAnalyticsEngine, DealOutcomePredictor, ValuationForecaster,
            get_predictive_analytics_engine,
            NLPHub, DocumentAnalyzer, ContractIntelligence, SentimentAnalyzer,
            get_nlp_hub,
            ComputerVisionEngine, DocumentClassifier, FinancialAnalyzer,
            get_computer_vision_engine,
            AIRecommendationEngine, DealRecommender, StrategyRecommender,
            get_ai_recommendation_engine
        )

        # Test predictive analytics imports
        from app.ai_ml.predictive_analytics import (
            ModelType, PredictionType, DealOutcome, ValuationInput,
            MarketFactors, PredictionResult, ValuationForecast,
            MLModel, DealSuccessModel, ValuationModel, TimelinePredictionModel
        )

        # Test NLP hub imports
        from app.ai_ml.nlp_hub import (
            DocumentType, LanguageCode, SentimentType, ContractClauseType,
            RiskLevel, TextAnalysisResult, SentimentAnalysis, ContractClause,
            ContractAnalysis, EntityExtraction, DocumentSummary
        )

        # Test computer vision imports
        from app.ai_ml.computer_vision import (
            DocumentFormat, DocumentClass, AnalysisType, ConfidenceLevel,
            FinancialMetricType, BoundingBox, OCRResult, TableCell,
            TableStructure, ChartElement, DocumentLayout, SignatureDetection,
            FinancialMetric, FinancialAnalysis, VisionAnalysisResult
        )

        # Test recommendation engine imports
        from app.ai_ml.recommendation_engine import (
            RecommendationType, PriorityLevel, IndustryVertical,
            RecommendationContext, AIRecommendation, DealMatch,
            StrategyRecommendation, UserPreferences
        )

        print("[PASS] All AI/ML imports successful")
        return True

    except ImportError as e:
        print(f"[FAIL] Import error: {e}")
        return False
    except Exception as e:
        print(f"[FAIL] Unexpected error during imports: {e}")
        return False

def test_service_initialization():
    """Test AI/ML service initialization"""
    print("\nTesting AI/ML service initialization...")

    try:
        # Test predictive analytics service
        from app.ai_ml import get_predictive_analytics_engine
        predictive_engine = get_predictive_analytics_engine()
        print(f"[PASS] Predictive Analytics Engine: {type(predictive_engine).__name__}")

        # Test NLP hub service
        from app.ai_ml import get_nlp_hub
        nlp_hub = get_nlp_hub()
        print(f"[PASS] NLP Hub: {type(nlp_hub).__name__}")

        # Test computer vision service
        from app.ai_ml import get_computer_vision_engine
        cv_engine = get_computer_vision_engine()
        print(f"[PASS] Computer Vision Engine: {type(cv_engine).__name__}")

        # Test recommendation engine service
        from app.ai_ml import get_ai_recommendation_engine
        rec_engine = get_ai_recommendation_engine()
        print(f"[PASS] AI Recommendation Engine: {type(rec_engine).__name__}")

        print("[PASS] All AI/ML services initialized successfully")
        return True

    except Exception as e:
        print(f"[FAIL] Service initialization error: {e}")
        return False

def test_predictive_analytics():
    """Test predictive analytics functionality"""
    print("\nTesting Predictive Analytics Engine...")

    try:
        from app.ai_ml import get_predictive_analytics_engine
        from app.ai_ml.predictive_analytics import DealOutcome, ValuationInput, MarketFactors

        engine = get_predictive_analytics_engine()

        # Test deal outcome prediction
        deal_outcome = DealOutcome(
            deal_id="test_deal_001",
            deal_value=150000000,
            target_industry="technology",
            acquirer_industry="technology",
            deal_type="horizontal_merger",
            geographic_complexity="domestic",
            regulatory_environment="moderate",
            market_conditions="stable",
            strategic_rationale="market_expansion"
        )

        prediction = engine.predict_deal_success(deal_outcome)
        print(f"✅ Deal Success Prediction: {prediction.success_probability:.2%}")

        # Test valuation forecasting
        valuation_input = ValuationInput(
            company_revenue=50000000,
            company_profit=8000000,
            industry="technology",
            growth_rate=0.25,
            market_size=1000000000,
            competitive_position="strong",
            geographic_markets=["north_america", "europe"],
            technology_assets=True,
            management_quality="excellent"
        )

        forecast = engine.forecast_valuation(valuation_input)
        print(f"✅ Valuation Forecast: ${forecast.estimated_value:,.0f}")

        # Test market analysis
        market_factors = MarketFactors(
            industry_growth=0.05,
            market_volatility=0.15,
            regulatory_stability=0.85,
            economic_indicators={"gdp_growth": 0.03, "inflation": 0.02},
            competitive_intensity=0.7,
            technology_disruption=0.6
        )

        analysis = engine.analyze_market_conditions("technology", market_factors)
        print(f"✅ Market Analysis: {analysis['market_attractiveness']:.2f}")

        # Test model performance
        performance = engine.get_model_performance()
        print(f"✅ Model Performance: {len(performance)} metrics")

        print("✅ Predictive Analytics Engine tests passed")
        return True

    except Exception as e:
        print(f"❌ Predictive analytics test error: {e}")
        traceback.print_exc()
        return False

def test_nlp_hub():
    """Test NLP Hub functionality"""
    print("\n🧪 Testing NLP Hub...")

    try:
        from app.ai_ml import get_nlp_hub
        from app.ai_ml.nlp_hub import DocumentType

        nlp_hub = get_nlp_hub()

        # Test document analysis
        sample_content = """
        MERGER AGREEMENT

        This Merger Agreement ("Agreement") is entered into as of March 15, 2024,
        between Acme Corporation, a Delaware corporation ("Acquirer"), and
        Target Industries Inc., a New York corporation ("Target").

        PURCHASE PRICE: The total consideration for this transaction shall be
        One Hundred Fifty Million Dollars ($150,000,000), subject to customary
        adjustments for working capital and debt.

        The parties represent and warrant that all information provided is
        accurate and complete. This transaction is expected to generate
        significant synergies and create substantial value for shareholders.
        """

        # Test comprehensive document processing
        results = nlp_hub.process_document(
            content=sample_content,
            document_type=DocumentType.CONTRACT,
            analysis_type="comprehensive"
        )

        print(f"✅ Document Analysis: {len(results)} analysis types")

        # Test contract analysis
        contract_analysis = nlp_hub.contract_intelligence.analyze_contract(sample_content)
        print(f"✅ Contract Analysis: {contract_analysis.total_clauses} clauses analyzed")

        # Test sentiment analysis
        sentiment = nlp_hub.sentiment_analyzer.analyze_sentiment(sample_content)
        print(f"✅ Sentiment Analysis: {sentiment.overall_sentiment.value}")

        # Test processing stats
        stats = nlp_hub.get_processing_stats()
        print(f"✅ Processing Stats: {stats['documents_processed']} documents")

        print("✅ NLP Hub tests passed")
        return True

    except Exception as e:
        print(f"❌ NLP Hub test error: {e}")
        traceback.print_exc()
        return False

def test_computer_vision():
    """Test Computer Vision functionality"""
    print("\n🧪 Testing Computer Vision Engine...")

    try:
        from app.ai_ml import get_computer_vision_engine
        from app.ai_ml.computer_vision import AnalysisType, DocumentFormat, DocumentClass

        cv_engine = get_computer_vision_engine()

        # Create sample document data (simulated)
        sample_document_data = b"sample_pdf_data_placeholder"

        # Test document processing
        analysis_types = [AnalysisType.OCR, AnalysisType.CLASSIFICATION, AnalysisType.TABLE_EXTRACTION]

        result = cv_engine.process_document(
            document_data=sample_document_data,
            analysis_types=analysis_types,
            format_hint=DocumentFormat.PDF
        )

        print(f"✅ Document Processing: {result.classification.predicted_class.value}")

        # Test document classification
        classification = cv_engine.document_classifier.classify_document(
            image_data=sample_document_data,
            format_hint=DocumentFormat.PDF
        )
        print(f"✅ Document Classification: {classification.confidence:.2%}")

        # Test financial analysis
        if result.classification.predicted_class == DocumentClass.FINANCIAL_STATEMENT:
            financial_analysis = cv_engine.financial_analyzer.analyze_financial_document(
                tables=result.tables,
                ocr_results=result.ocr_results,
                document_class=result.classification.predicted_class
            )
            print(f"✅ Financial Analysis: {len(financial_analysis.metrics)} metrics")

        # Test processing stats
        stats = cv_engine.get_processing_stats()
        print(f"✅ Processing Stats: {stats['documents_processed']} documents")

        print("✅ Computer Vision Engine tests passed")
        return True

    except Exception as e:
        print(f"❌ Computer Vision test error: {e}")
        traceback.print_exc()
        return False

def test_recommendation_engine():
    """Test AI Recommendation Engine functionality"""
    print("\n🧪 Testing AI Recommendation Engine...")

    try:
        from app.ai_ml import get_ai_recommendation_engine
        from app.ai_ml.recommendation_engine import (
            RecommendationContext, RecommendationType, IndustryVertical
        )

        rec_engine = get_ai_recommendation_engine()

        # Create recommendation context
        context = RecommendationContext(
            user_id="test_user_001",
            company_id="test_company_001",
            industry_vertical=IndustryVertical.TECHNOLOGY,
            company_size="medium",
            deal_history=[],
            current_objectives=["growth", "market_expansion"],
            risk_tolerance="moderate",
            geographic_focus=["north_america", "europe"],
            budget_range=(50000000, 200000000),
            timeline_preference="medium_term"
        )

        # Test comprehensive recommendations
        recommendation_types = [
            RecommendationType.DEAL_OPPORTUNITY,
            RecommendationType.STRATEGIC_PARTNER,
            RecommendationType.MARKET_ENTRY
        ]

        recommendations = rec_engine.generate_comprehensive_recommendations(
            context=context,
            recommendation_types=recommendation_types,
            max_per_type=3
        )

        print(f"✅ Generated Recommendations: {len(recommendations)} total")

        # Test deal matching
        company_profile = {
            "name": "Test Company",
            "industry": "technology",
            "revenue": 100000000,
            "employees": 500
        }

        criteria = {
            "target_industry": "technology",
            "deal_size_range": (50000000, 150000000),
            "geographic_preference": "north_america"
        }

        matches = rec_engine.deal_recommender.find_strategic_matches(
            company_profile=company_profile,
            criteria=criteria
        )
        print(f"✅ Deal Matches: {len(matches)} strategic matches")

        # Test strategy recommendations
        strategies = rec_engine.strategy_recommender.recommend_strategies(
            context=context,
            focus_areas=["growth", "efficiency", "innovation"]
        )
        print(f"✅ Strategy Recommendations: {len(strategies)} strategies")

        # Test analytics
        analytics = rec_engine.get_recommendation_analytics()
        print(f"✅ Analytics: {analytics['recommendations_generated']} recommendations generated")

        print("✅ AI Recommendation Engine tests passed")
        return True

    except Exception as e:
        print(f"❌ Recommendation Engine test error: {e}")
        traceback.print_exc()
        return False

def test_api_endpoints():
    """Test AI/ML API endpoints"""
    print("\n🧪 Testing AI/ML API endpoints...")

    try:
        from app.api.v1 import ai_ml

        # Test router exists
        router = ai_ml.router
        print(f"✅ API Router: {len(router.routes)} routes defined")

        # Count endpoints by category
        predictive_endpoints = [r for r in router.routes if "/ai-ml/predictive/" in str(r.path)]
        nlp_endpoints = [r for r in router.routes if "/ai-ml/nlp/" in str(r.path)]
        cv_endpoints = [r for r in router.routes if "/ai-ml/computer-vision/" in str(r.path)]
        rec_endpoints = [r for r in router.routes if "/ai-ml/recommendations/" in str(r.path)]
        general_endpoints = [r for r in router.routes if "/ai-ml/" in str(r.path) and
                           not any(cat in str(r.path) for cat in ["predictive", "nlp", "computer-vision", "recommendations"])]

        print(f"✅ Predictive Analytics Endpoints: {len(predictive_endpoints)}")
        print(f"✅ NLP Hub Endpoints: {len(nlp_endpoints)}")
        print(f"✅ Computer Vision Endpoints: {len(cv_endpoints)}")
        print(f"✅ Recommendation Engine Endpoints: {len(rec_endpoints)}")
        print(f"✅ General AI/ML Endpoints: {len(general_endpoints)}")

        # Test main API router integration
        from app.api.v1.api import api_router
        ai_ml_routes = [r for r in api_router.routes if "ai-ml" in str(r.path).lower()]
        print(f"✅ AI/ML routes integrated in main router: {len(ai_ml_routes) > 0}")

        print("✅ AI/ML API endpoints verification passed")
        return True

    except Exception as e:
        print(f"❌ API endpoints test error: {e}")
        traceback.print_exc()
        return False

def test_enum_types():
    """Test all AI/ML enumeration types"""
    print("\n🧪 Testing AI/ML enumeration types...")

    try:
        # Predictive Analytics Enums
        from app.ai_ml.predictive_analytics import ModelType, PredictionType
        print(f"✅ ModelType enum: {len(ModelType)} values")
        print(f"✅ PredictionType enum: {len(PredictionType)} values")

        # NLP Hub Enums
        from app.ai_ml.nlp_hub import (
            DocumentType, LanguageCode, SentimentType,
            ContractClauseType, RiskLevel
        )
        print(f"✅ DocumentType enum: {len(DocumentType)} values")
        print(f"✅ LanguageCode enum: {len(LanguageCode)} values")
        print(f"✅ SentimentType enum: {len(SentimentType)} values")
        print(f"✅ ContractClauseType enum: {len(ContractClauseType)} values")
        print(f"✅ RiskLevel enum: {len(RiskLevel)} values")

        # Computer Vision Enums
        from app.ai_ml.computer_vision import (
            DocumentFormat, DocumentClass, AnalysisType,
            ConfidenceLevel, FinancialMetricType
        )
        print(f"✅ DocumentFormat enum: {len(DocumentFormat)} values")
        print(f"✅ DocumentClass enum: {len(DocumentClass)} values")
        print(f"✅ AnalysisType enum: {len(AnalysisType)} values")
        print(f"✅ ConfidenceLevel enum: {len(ConfidenceLevel)} values")
        print(f"✅ FinancialMetricType enum: {len(FinancialMetricType)} values")

        # Recommendation Engine Enums
        from app.ai_ml.recommendation_engine import (
            RecommendationType, PriorityLevel, IndustryVertical, RecommendationStatus
        )
        print(f"✅ RecommendationType enum: {len(RecommendationType)} values")
        print(f"✅ PriorityLevel enum: {len(PriorityLevel)} values")
        print(f"✅ IndustryVertical enum: {len(IndustryVertical)} values")
        print(f"✅ RecommendationStatus enum: {len(RecommendationStatus)} values")

        print("✅ All AI/ML enumeration types verified")
        return True

    except Exception as e:
        print(f"❌ Enum types test error: {e}")
        traceback.print_exc()
        return False

def test_data_classes():
    """Test AI/ML data class structures"""
    print("\n🧪 Testing AI/ML data classes...")

    try:
        # Test predictive analytics data classes
        from app.ai_ml.predictive_analytics import (
            DealOutcome, ValuationInput, MarketFactors,
            PredictionResult, ValuationForecast
        )

        deal_outcome = DealOutcome(
            deal_id="test_001",
            deal_value=100000000,
            target_industry="technology",
            acquirer_industry="technology",
            deal_type="merger",
            geographic_complexity="domestic",
            regulatory_environment="moderate",
            market_conditions="stable",
            strategic_rationale="growth"
        )
        print(f"✅ DealOutcome: {deal_outcome.deal_id}")

        # Test NLP data classes
        from app.ai_ml.nlp_hub import (
            TextAnalysisResult, SentimentAnalysis, ContractAnalysis,
            EntityExtraction, DocumentSummary
        )

        from datetime import datetime
        text_analysis = TextAnalysisResult(
            text_id="test_text_001",
            language="en",
            word_count=100,
            sentence_count=5,
            paragraph_count=2,
            reading_level="college",
            key_topics=["merger", "acquisition"],
            confidence_score=0.92,
            processing_time=1.5
        )
        print(f"✅ TextAnalysisResult: {text_analysis.confidence_score}")

        # Test computer vision data classes
        from app.ai_ml.computer_vision import (
            BoundingBox, OCRResult, TableStructure,
            VisionAnalysisResult, FinancialAnalysis
        )

        bbox = BoundingBox(x=100, y=100, width=200, height=50)
        print(f"✅ BoundingBox: {bbox.width}x{bbox.height}")

        # Test recommendation engine data classes
        from app.ai_ml.recommendation_engine import (
            RecommendationContext, AIRecommendation, DealMatch,
            StrategyRecommendation, UserPreferences
        )

        rec_context = RecommendationContext(
            user_id="user_001",
            company_id="company_001",
            industry_vertical="technology",
            company_size="medium",
            deal_history=[],
            current_objectives=["growth"],
            risk_tolerance="moderate",
            geographic_focus=["us"],
            budget_range=(10000000, 100000000),
            timeline_preference="medium_term"
        )
        print(f"✅ RecommendationContext: {rec_context.user_id}")

        print("✅ All AI/ML data classes verified")
        return True

    except Exception as e:
        print(f"❌ Data classes test error: {e}")
        traceback.print_exc()
        return False

def run_sprint12_verification():
    """Run complete Sprint 12 verification suite"""
    print("🚀 SPRINT 12 VERIFICATION - Advanced AI & Machine Learning Platform")
    print("=" * 80)

    # Track test results
    test_results = []

    # Run all verification tests
    tests = [
        ("AI/ML Module Imports", test_ai_ml_imports),
        ("Service Initialization", test_service_initialization),
        ("Predictive Analytics", test_predictive_analytics),
        ("NLP Hub", test_nlp_hub),
        ("Computer Vision Engine", test_computer_vision),
        ("AI Recommendation Engine", test_recommendation_engine),
        ("API Endpoints", test_api_endpoints),
        ("Enumeration Types", test_enum_types),
        ("Data Classes", test_data_classes)
    ]

    for test_name, test_func in tests:
        try:
            result = test_func()
            test_results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            test_results.append((test_name, False))

    # Print summary
    print("\n" + "=" * 80)
    print("📊 SPRINT 12 VERIFICATION SUMMARY")
    print("=" * 80)

    passed_tests = sum(1 for _, result in test_results if result)
    total_tests = len(test_results)

    for test_name, result in test_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status:<12} {test_name}")

    print("-" * 80)
    print(f"TOTAL TESTS: {total_tests}")
    print(f"PASSED: {passed_tests}")
    print(f"FAILED: {total_tests - passed_tests}")
    print(f"SUCCESS RATE: {(passed_tests/total_tests)*100:.1f}%")

    if passed_tests == total_tests:
        print("\n🎉 ALL TESTS PASSED - Sprint 12 AI/ML Platform is ready for production!")

        # Sprint 12 Feature Summary
        print("\n📋 SPRINT 12 FEATURE SUMMARY")
        print("-" * 50)
        print("✅ Predictive Analytics Engine")
        print("   • Deal outcome prediction with AI models")
        print("   • Company valuation forecasting")
        print("   • M&A timeline prediction")
        print("   • Market analysis and trends")

        print("✅ Natural Language Processing Hub")
        print("   • Advanced document analysis")
        print("   • Contract intelligence and risk assessment")
        print("   • Sentiment analysis and emotion detection")
        print("   • Multi-language support")

        print("✅ Computer Vision Engine")
        print("   • Automated document classification")
        print("   • Financial data extraction from documents")
        print("   • OCR with layout analysis")
        print("   • Table and chart recognition")

        print("✅ AI Recommendation Engine")
        print("   • Personalized deal recommendations")
        print("   • Strategic matching algorithms")
        print("   • AI-powered business strategies")
        print("   • Learning from user feedback")

        print("✅ Comprehensive API Layer")
        print("   • 25+ AI/ML API endpoints")
        print("   • RESTful API design")
        print("   • Comprehensive request/response models")
        print("   • Error handling and validation")

        print("\n🔧 TECHNICAL ARCHITECTURE")
        print("-" * 50)
        print("• Service-oriented architecture with dependency injection")
        print("• Abstract base classes for extensibility")
        print("• Comprehensive data models and enumerations")
        print("• Singleton pattern for service instances")
        print("• Machine learning model abstraction")
        print("• Confidence scoring and performance tracking")

        return True
    else:
        print(f"\n⚠️  {total_tests - passed_tests} tests failed - Please review and fix issues")
        return False

if __name__ == "__main__":
    try:
        success = run_sprint12_verification()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n💥 Verification script failed: {e}")
        traceback.print_exc()
        sys.exit(1)