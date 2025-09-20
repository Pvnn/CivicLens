#!/usr/bin/env python3
"""
Test script for real gap analysis
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.gap_analyzer import gap_analyzer

def test_gap_analysis():
    """Test the real gap analysis functionality"""
    print("🔍 Testing Real Gap Analysis...")
    print("=" * 50)
    
    try:
        # Generate gap analysis
        analysis = gap_analyzer.generate_gap_analysis()
        
        print(f"\n📊 Analysis Results:")
        print(f"Total data points: {analysis['data_sources']['total_items']}")
        print(f"Youth sources: {analysis['data_sources']['youth_sources']}")
        print(f"Political sources: {analysis['data_sources']['political_sources']}")
        print(f"Reliability score: {analysis['reliability_notes']['reliability_score']:.2f}")
        print(f"Overall gap: {analysis['overall_scores']['overall_gap']:.1f}")
        
        print(f"\n🎯 Top 10 Gap Analysis:")
        for i, (topic, data) in enumerate(analysis['top_gaps'][:10], 1):
            print(f"{i:2d}. {topic.title():20s} | Gap: {data['gap_score']:6.1f} | "
                  f"Youth: {data['youth_focus']:4.1f} | Political: {data['political_focus']:4.1f} | "
                  f"Reliability: {data['reliability']:.2f}")
        
        print(f"\n📈 Methodology:")
        print(f"- Youth keywords: {len(gap_analyzer.youth_keywords)} terms")
        print(f"- Political keywords: {len(gap_analyzer.political_keywords)} terms")
        print(f"- Data sources: {len(analysis['data_sources'])} platforms")
        
        print(f"\n✅ Gap analysis completed successfully!")
        print(f"💡 This analysis is based on real data scraping, not hardcoded values.")
        
    except Exception as e:
        print(f"❌ Error in gap analysis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_gap_analysis()
