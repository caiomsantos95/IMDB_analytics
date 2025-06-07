#!/usr/bin/env python3
"""
IMDb Ratings Analysis: A 14-Year Cinematic Journey
==================================================

Comprehensive analysis script for IMDb ratings data that generates:
- Statistical analysis of viewing patterns
- Year-over-year evolution insights
- Director and genre preferences
- Comprehensive visualizations

Author: Generated with Claude Code
Date: June 2025
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import re
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class IMDbAnalyzer:
    """Main class for analyzing IMDb ratings data"""
    
    def __init__(self, csv_path):
        """Initialize with path to IMDb CSV export"""
        self.csv_path = csv_path
        self.df = None
        self.yearly_stats = None
        self.director_analysis = None
        
    def load_data(self):
        """Load and prepare the IMDb data"""
        print("Loading IMDb ratings data...")
        self.df = pd.read_csv(self.csv_path)
        
        # Convert date columns
        self.df['Date Rated'] = pd.to_datetime(self.df['Date Rated'])
        self.df['Release Date'] = pd.to_datetime(self.df['Release Date'], errors='coerce')
        self.df['Rating Year'] = self.df['Date Rated'].dt.year
        self.df['Content_Age'] = datetime.now().year - self.df['Year']
        
        print(f"Loaded {len(self.df)} ratings from {self.df['Date Rated'].min().date()} to {self.df['Date Rated'].max().date()}")
        
    def basic_statistics(self):
        """Generate basic statistics about the dataset"""
        stats = {
            'total_entries': len(self.df),
            'movies': len(self.df[self.df['Title Type'] == 'Movie']),
            'tv_series': len(self.df[self.df['Title Type'] == 'TV Series']),
            'tv_episodes': len(self.df[self.df['Title Type'] == 'TV Episode']),
            'avg_rating': self.df['Your Rating'].mean(),
            'most_common_rating': self.df['Your Rating'].mode().iloc[0],
            'imdb_correlation': self.df['Your Rating'].corr(self.df['IMDb Rating'])
        }
        
        print("\n=== BASIC STATISTICS ===")
        print(f"Total entries: {stats['total_entries']}")
        print(f"Movies: {stats['movies']} ({stats['movies']/stats['total_entries']*100:.1f}%)")
        print(f"TV Series: {stats['tv_series']} ({stats['tv_series']/stats['total_entries']*100:.1f}%)")
        print(f"TV Episodes: {stats['tv_episodes']} ({stats['tv_episodes']/stats['total_entries']*100:.1f}%)")
        print(f"Average rating: {stats['avg_rating']:.2f}")
        print(f"Most common rating: {stats['most_common_rating']}")
        print(f"IMDb correlation: {stats['imdb_correlation']:.3f}")
        
        return stats
        
    def yearly_evolution(self):
        """Analyze year-over-year patterns"""
        self.yearly_stats = self.df.groupby('Rating Year').agg({
            'Your Rating': ['count', 'mean', 'std'],
            'IMDb Rating': 'mean',
            'Year': 'mean',
            'Content_Age': 'mean'
        }).round(2)
        
        self.yearly_stats.columns = ['Count', 'Avg_Your_Rating', 'Std_Your_Rating', 
                                   'Avg_IMDb_Rating', 'Avg_Content_Year', 'Avg_Content_Age']
        
        print("\n=== YEAR-OVER-YEAR EVOLUTION ===")
        print(self.yearly_stats)
        
        return self.yearly_stats
        
    def analyze_directors(self):
        """Analyze director preferences and patterns"""
        # Clean and extract directors
        director_list = []
        for directors in self.df['Directors'].fillna(''):
            if directors:
                directors_split = [d.strip() for d in str(directors).split(',')]
                director_list.extend(directors_split)
        
        director_counts = Counter(director_list)
        top_directors = director_counts.most_common(15)
        
        # Detailed analysis for top directors
        self.director_analysis = []
        for director, count in top_directors:
            if director and count >= 5:  # Only directors with 5+ works
                director_works = self.df[self.df['Directors'].str.contains(director, na=False)]
                self.director_analysis.append({
                    'Director': director,
                    'Count': count,
                    'Avg_Rating': director_works['Your Rating'].mean(),
                    'Std_Rating': director_works['Your Rating'].std(),
                    'Latest_Work': director_works['Date Rated'].max().strftime('%Y-%m-%d')
                })
        
        director_df = pd.DataFrame(self.director_analysis)
        
        print("\n=== FAVORITE DIRECTORS ===")
        print("Top Directors by Average Rating:")
        for _, row in director_df.sort_values('Avg_Rating', ascending=False).head(10).iterrows():
            print(f"{row['Director']}: {row['Avg_Rating']:.2f} avg ({row['Count']} works)")
            
        return director_df
        
    def analyze_genres(self):
        """Analyze genre preferences"""
        genre_list = []
        for genres in self.df['Genres'].fillna(''):
            if genres:
                genre_split = [g.strip() for g in str(genres).split(',')]
                genre_list.extend(genre_split)
        
        genre_counts = Counter(genre_list)
        top_genres = genre_counts.most_common(15)
        
        print("\n=== GENRE ANALYSIS ===")
        print("Top Genres by frequency:")
        for genre, count in top_genres:
            if genre:
                genre_ratings = self.df[self.df['Genres'].str.contains(genre, na=False)]['Your Rating']
                avg_rating = genre_ratings.mean()
                percentage = (count / len(self.df)) * 100
                print(f"{genre}: {count} works ({percentage:.1f}%), avg rating: {avg_rating:.2f}")
                
        return top_genres
        
    def rating_patterns(self):
        """Analyze rating distribution and patterns"""
        print("\n=== RATING PATTERNS ===")
        
        # Rating distribution
        rating_dist = self.df['Your Rating'].value_counts().sort_index()
        print("Rating distribution:")
        for rating, count in rating_dist.items():
            percentage = (count / len(self.df)) * 100
            print(f"{rating}/10: {count} ratings ({percentage:.1f}%)")
        
        # High vs low ratings
        high_ratings = len(self.df[self.df['Your Rating'] >= 8])
        low_ratings = len(self.df[self.df['Your Rating'] <= 5])
        
        print(f"\nHigh ratings (8+): {high_ratings} ({high_ratings/len(self.df)*100:.1f}%)")
        print(f"Low ratings (≤5): {low_ratings} ({low_ratings/len(self.df)*100:.1f}%)")
        
        return rating_dist
        
    def content_age_analysis(self):
        """Analyze preferences by content age"""
        self.df['Age_Group'] = pd.cut(self.df['Content_Age'], 
                                    bins=[-1, 5, 15, 30, 50, 100], 
                                    labels=['Very Recent (0-5y)', 'Recent (6-15y)', 
                                          'Older (16-30y)', 'Classic (31-50y)', 'Very Classic (50y+)'])
        
        age_stats = self.df.groupby('Age_Group')['Your Rating'].agg(['count', 'mean']).round(2)
        
        print("\n=== CONTENT AGE PREFERENCES ===")
        print(age_stats)
        
        return age_stats
        
    def create_visualizations(self, save_path='imdb_analysis_charts.png'):
        """Create comprehensive visualizations"""
        # Set style
        sns.set_style("whitegrid")
        sns.set_palette("husl")
        
        # Create comprehensive visualization
        fig = plt.figure(figsize=(20, 16))
        
        # 1. YoY Volume and Rating Evolution
        ax1 = plt.subplot(3, 3, 1)
        years = self.yearly_stats.index
        ax1_twin = ax1.twinx()
        
        # Volume bars and rating line
        ax1.bar(years, self.yearly_stats['Count'], alpha=0.7, color='steelblue', width=0.6)
        ax1_twin.plot(years, self.yearly_stats['Avg_Your_Rating'], 'ro-', linewidth=3, markersize=8)
        
        ax1.set_xlabel('Year')
        ax1.set_ylabel('Number of Ratings', color='steelblue')
        ax1_twin.set_ylabel('Average Rating', color='red')
        ax1.set_title('Rating Volume & Quality Evolution', fontsize=14, fontweight='bold')
        ax1.tick_params(axis='x', rotation=45)
        ax1_twin.set_ylim(6.5, 8.5)
        
        # 2. Content Age Evolution
        ax2 = plt.subplot(3, 3, 2)
        ax2.plot(years, self.yearly_stats['Avg_Content_Age'], 'go-', linewidth=3, markersize=8)
        ax2.set_xlabel('Year')
        ax2.set_ylabel('Avg Age of Content (years)')
        ax2.set_title('Content Age Preferences Over Time', fontsize=14, fontweight='bold')
        ax2.tick_params(axis='x', rotation=45)
        ax2.grid(True, alpha=0.3)
        
        # 3. Rating Distribution
        ax3 = plt.subplot(3, 3, 3)
        rating_dist = self.df['Your Rating'].value_counts().sort_index()
        ax3.bar(rating_dist.index, rating_dist.values, color='purple', alpha=0.7)
        ax3.set_xlabel('Rating')
        ax3.set_ylabel('Frequency')
        ax3.set_title('Rating Distribution', fontsize=14, fontweight='bold')
        
        # 4. Your vs IMDb Rating
        ax4 = plt.subplot(3, 3, 4)
        ax4.scatter(self.df['IMDb Rating'], self.df['Your Rating'], alpha=0.4, s=20)
        ax4.plot([4, 10], [4, 10], 'r--', alpha=0.8, label='Perfect correlation')
        correlation = self.df['Your Rating'].corr(self.df['IMDb Rating'])
        ax4.set_xlabel('IMDb Rating')
        ax4.set_ylabel('Your Rating')
        ax4.set_title(f'Your vs IMDb Ratings (r={correlation:.3f})', fontsize=14, fontweight='bold')
        ax4.legend()
        
        # 5. Top Directors Bar Chart
        ax5 = plt.subplot(3, 3, 5)
        if self.director_analysis:
            director_df = pd.DataFrame(self.director_analysis)
            top_directors = director_df.nlargest(10, 'Avg_Rating')
            bars = ax5.barh(range(len(top_directors)), top_directors['Avg_Rating'], 
                          color=plt.cm.viridis(top_directors['Avg_Rating']/10))
            ax5.set_yticks(range(len(top_directors)))
            ax5.set_yticklabels(top_directors['Director'])
            ax5.set_xlabel('Average Rating')
            ax5.set_title('Top Directors by Average Rating', fontsize=14, fontweight='bold')
            ax5.set_xlim(6, 10)
        
        # 6. Genre Evolution
        ax6 = plt.subplot(3, 3, 6)
        top_genres = ['Drama', 'Action', 'Sci-Fi', 'Comedy', 'Thriller']
        genre_by_year = {}
        
        for genre in top_genres:
            genre_by_year[genre] = []
            for year in sorted(self.df['Rating Year'].unique()):
                year_data = self.df[self.df['Rating Year'] == year]
                genre_count = len(year_data[year_data['Genres'].str.contains(genre, na=False)])
                total_count = len(year_data)
                percentage = (genre_count / total_count) * 100 if total_count > 0 else 0
                genre_by_year[genre].append(percentage)
        
        years_sorted = sorted(self.df['Rating Year'].unique())
        for genre in top_genres:
            ax6.plot(years_sorted, genre_by_year[genre], marker='o', label=genre, linewidth=2)
        
        ax6.set_xlabel('Year')
        ax6.set_ylabel('Percentage of Ratings')
        ax6.set_title('Genre Preferences Evolution', fontsize=14, fontweight='bold')
        ax6.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax6.tick_params(axis='x', rotation=45)
        
        # 7. Cumulative Ratings
        ax7 = plt.subplot(3, 3, 7)
        cumulative_ratings = self.yearly_stats['Count'].cumsum()
        ax7.plot(self.yearly_stats.index, cumulative_ratings, 'mo-', linewidth=3, markersize=8)
        ax7.set_xlabel('Year')
        ax7.set_ylabel('Cumulative Ratings')
        ax7.set_title('Total Ratings Over Time', fontsize=14, fontweight='bold')
        ax7.tick_params(axis='x', rotation=45)
        ax7.grid(True, alpha=0.3)
        
        # 8. Rating Generosity
        ax8 = plt.subplot(3, 3, 8)
        generosity_by_year = []
        years_list = sorted(self.df['Rating Year'].unique())
        
        for year in years_list:
            year_data = self.df[self.df['Rating Year'] == year]
            high_ratings = len(year_data[year_data['Your Rating'] >= 8])
            total_ratings = len(year_data)
            generosity = (high_ratings / total_ratings) * 100 if total_ratings > 0 else 0
            generosity_by_year.append(generosity)
        
        ax8.plot(years_list, generosity_by_year, 'co-', linewidth=3, markersize=8)
        ax8.set_xlabel('Year')
        ax8.set_ylabel('% of Ratings 8+')
        ax8.set_title('Rating Generosity Over Time', fontsize=14, fontweight='bold')
        ax8.tick_params(axis='x', rotation=45)
        ax8.grid(True, alpha=0.3)
        
        # 9. Content Type Distribution
        ax9 = plt.subplot(3, 3, 9)
        content_types = self.df['Title Type'].value_counts()
        colors = plt.cm.Set3(np.linspace(0, 1, len(content_types)))
        wedges, texts, autotexts = ax9.pie(content_types.values, labels=content_types.index, 
                                          autopct='%1.1f%%', colors=colors)
        ax9.set_title('Content Type Distribution', fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"\nVisualization saved as '{save_path}'")
        
    def generate_insights(self):
        """Generate comprehensive insights about viewing patterns"""
        stats = self.basic_statistics()
        
        print("\n=== VIEWING TASTE CHARACTERIZATION ===")
        
        # Calculate key metrics
        avg_rating = stats['avg_rating']
        imdb_correlation = stats['imdb_correlation']
        
        # Rating generosity
        generous_threshold = 7
        generous_percentage = len(self.df[self.df['Your Rating'] >= generous_threshold]) / len(self.df) * 100
        
        print(f"Average rating: {avg_rating:.2f}")
        print(f"IMDb correlation: {imdb_correlation:.3f} ({'Strong' if abs(imdb_correlation) > 0.7 else 'Moderate' if abs(imdb_correlation) > 0.4 else 'Weak'} alignment)")
        print(f"Rating generosity: {generous_percentage:.1f}% of ratings are {generous_threshold}+")
        
        if generous_percentage > 60:
            generosity = "Very generous"
        elif generous_percentage > 40:
            generosity = "Moderately generous"  
        else:
            generosity = "Selective"
            
        print(f"Overall rating style: {generosity}")
        
        # Evolution insights
        peak_volume_year = self.yearly_stats['Count'].idxmax()
        peak_quality_year = self.yearly_stats['Avg_Your_Rating'].idxmax()
        
        print(f"\nEvolution insights:")
        print(f"Peak volume year: {peak_volume_year} ({self.yearly_stats.loc[peak_volume_year, 'Count']} ratings)")
        print(f"Peak quality year: {peak_quality_year} ({self.yearly_stats.loc[peak_quality_year, 'Avg_Your_Rating']:.2f} avg)")
        
        return {
            'avg_rating': avg_rating,
            'correlation': imdb_correlation,
            'generosity': generous_percentage,
            'style': generosity,
            'peak_volume_year': peak_volume_year,
            'peak_quality_year': peak_quality_year
        }
        
    def run_complete_analysis(self, visualization_path='imdb_analysis_complete.png'):
        """Run the complete analysis pipeline"""
        print("🎬 Starting Complete IMDb Analysis 🎬")
        print("=" * 50)
        
        # Load and prepare data
        self.load_data()
        
        # Run all analyses
        basic_stats = self.basic_statistics()
        yearly_data = self.yearly_evolution()
        director_data = self.analyze_directors()
        genre_data = self.analyze_genres()
        rating_patterns = self.rating_patterns()
        age_data = self.content_age_analysis()
        insights = self.generate_insights()
        
        # Create visualizations
        self.create_visualizations(visualization_path)
        
        print("\n" + "=" * 50)
        print("🎯 Analysis Complete! 🎯")
        print(f"📊 Visualization saved: {visualization_path}")
        
        return {
            'basic_stats': basic_stats,
            'yearly_data': yearly_data,
            'director_data': director_data,
            'genre_data': genre_data,
            'insights': insights
        }


def main():
    """Main function to run the analysis"""
    # Path to your IMDb CSV export
    csv_path = '/Users/caiodossantos/Downloads/3e9726f2-326c-43b5-9bbe-c0ce9864051e.csv'
    
    # Create analyzer instance
    analyzer = IMDbAnalyzer(csv_path)
    
    # Run complete analysis
    results = analyzer.run_complete_analysis('imdb_analysis_complete.png')
    
    return analyzer, results


if __name__ == "__main__":
    analyzer, results = main()