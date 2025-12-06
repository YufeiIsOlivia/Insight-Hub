#!/usr/bin/env python3
"""
Generate data visualization figures (Figures 2-5) for the project report.
Note: Figure 1 (System Architecture) should be created using draw.io or similar tools.
"""

import matplotlib.pyplot as plt
import numpy as np
import os

# Create figures directory
os.makedirs('evaluation/figures', exist_ok=True)

# Set style for professional academic papers - 3x larger fonts for paper publication
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['figure.figsize'] = (14, 10)  # Much larger figure size
plt.rcParams['font.size'] = 42  # Base font size (14 * 3)
plt.rcParams['font.family'] = 'serif'
plt.rcParams['axes.labelsize'] = 30  # Axis labels
plt.rcParams['axes.titlesize'] = 40  # Title
plt.rcParams['xtick.labelsize'] = 30  # X-axis ticks
plt.rcParams['ytick.labelsize'] = 30  # Y-axis ticks
plt.rcParams['legend.fontsize'] = 42
plt.rcParams['figure.dpi'] = 300
plt.rcParams['axes.linewidth'] = 3.0  # Much thicker axes (1.5 * 2)
plt.rcParams['grid.linewidth'] = 2.0
plt.rcParams['xtick.major.width'] = 3.0
plt.rcParams['ytick.major.width'] = 3.0
plt.rcParams['xtick.major.size'] = 10
plt.rcParams['ytick.major.size'] = 10

# Data from evaluation results
models = ['Claude 3.5\nSonnet', 'GPT-3.5\nTurbo', 'Gemini 2.5\nFlash']
relevance_scores = [3.82, 3.68, 3.94]
faithfulness_scores = [3.96, 3.58, 4.20]
answer_quality_scores = [4.12, 3.70, 4.32]
response_times = [10.84, 3.64, 2.17]

# Professional color palette
colors = ['#2E86AB', '#A23B72', '#F18F01']

def create_bar_chart(models, scores, ylabel, title, filename, ylim=(0, 5), yticks=None):
    """Create a professional bar chart with 3x larger fonts for paper publication."""
    fig, ax = plt.subplots(figsize=(14, 10))  # Much larger figure size
    
    bars = ax.bar(models, scores, color=colors, alpha=0.85, 
                  edgecolor='black', linewidth=4.0, width=0.6)
    
    ax.set_ylabel(ylabel, fontsize=30, fontweight='bold')
    ax.set_xlabel('Model', fontsize=30, fontweight='bold')
    ax.set_title(title, fontsize=40, fontweight='bold', pad=40)
    ax.set_ylim(ylim)
    
    if yticks is not None:
        ax.set_yticks(yticks)
    else:
        ax.set_yticks(np.arange(ylim[0], ylim[1] + 0.5, 0.5))
    
    # Make tick labels (coordinates)
    ax.tick_params(axis='x', labelsize=30, width=3.0, length=12, pad=15)
    ax.tick_params(axis='y', labelsize=30, width=3.0, length=12, pad=15)
    
    ax.grid(axis='y', alpha=0.3, linestyle='--', linewidth=2.5)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_linewidth(3.0)
    ax.spines['bottom'].set_linewidth(3.0)
    
    # Add value labels on bars
    for bar, score in zip(bars, scores):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + (ylim[1] - ylim[0]) * 0.02,
                f'{score:.2f}',
                ha='center', va='bottom', fontsize=30, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(f'evaluation/figures/{filename}', dpi=300, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    plt.close()
    print(f"✓ Created {filename}")

# Generate data visualization figures
print("Generating data visualization figures...")
print("=" * 60)

create_bar_chart(models, relevance_scores, 
                 'Retrieval Relevance Score', 
                 'Retrieval Relevance Scores by Model',
                 'figure_2_retrieval_relevance.png')

create_bar_chart(models, faithfulness_scores,
                 'Faithfulness Score',
                 'Faithfulness Scores by Model',
                 'figure_3_faithfulness.png')

create_bar_chart(models, answer_quality_scores,
                 'Answer Quality Score',
                 'Answer Quality Scores by Model',
                 'figure_4_answer_quality.png')

create_bar_chart(models, response_times,
                 'Average Response Time (seconds)',
                 'Average Response Time by Model',
                 'figure_5_response_time.png',
                 ylim=(0, 12),
                 yticks=np.arange(0, 13, 1))

print("=" * 60)
print("Data visualization figures generated successfully!")
print("\nNote: Figure 1 (System Architecture) should be created using:")
print("  - draw.io / diagrams.net (recommended)")
print("  - Mermaid (for Markdown)")
print("  - Lucidchart or similar professional tools")
print("\nSee figure_descriptions.md for detailed instructions.")

