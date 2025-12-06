#!/usr/bin/env python3
"""
Generate all figures for the project report.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
plt.rcParams['figure.figsize'] = (10, 6)
plt.rcParams['font.size'] = 11
plt.rcParams['axes.labelsize'] = 12
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['xtick.labelsize'] = 10
plt.rcParams['ytick.labelsize'] = 10
plt.rcParams['legend.fontsize'] = 10

# Data from evaluation results
models = ['Claude 3.5\nSonnet', 'GPT-3.5\nTurbo', 'Gemini 2.5\nFlash']
relevance_scores = [3.82, 3.68, 3.94]
faithfulness_scores = [3.96, 3.58, 4.20]
answer_quality_scores = [4.12, 3.70, 4.32]
response_times = [10.84, 3.64, 2.17]

# Colors for different models
colors = ['#2E86AB', '#A23B72', '#F18F01']

# Figure 2: Retrieval Relevance Scores
def create_figure_2():
    fig, ax = plt.subplots(figsize=(8, 6))
    bars = ax.bar(models, relevance_scores, color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)
    ax.set_ylabel('Retrieval Relevance Score', fontsize=12, fontweight='bold')
    ax.set_xlabel('Model', fontsize=12, fontweight='bold')
    ax.set_title('Retrieval Relevance Scores by Model', fontsize=14, fontweight='bold', pad=20)
    ax.set_ylim(0, 5)
    ax.set_yticks(np.arange(0, 5.5, 0.5))
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    # Add value labels on bars
    for i, (bar, score) in enumerate(zip(bars, relevance_scores)):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.05,
                f'{score:.2f}',
                ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('evaluation/figures/figure_2_retrieval_relevance.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ Created Figure 2: Retrieval Relevance Scores")

# Figure 3: Faithfulness Scores
def create_figure_3():
    fig, ax = plt.subplots(figsize=(8, 6))
    bars = ax.bar(models, faithfulness_scores, color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)
    ax.set_ylabel('Faithfulness Score', fontsize=12, fontweight='bold')
    ax.set_xlabel('Model', fontsize=12, fontweight='bold')
    ax.set_title('Faithfulness Scores by Model', fontsize=14, fontweight='bold', pad=20)
    ax.set_ylim(0, 5)
    ax.set_yticks(np.arange(0, 5.5, 0.5))
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    # Add value labels on bars
    for i, (bar, score) in enumerate(zip(bars, faithfulness_scores)):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.05,
                f'{score:.2f}',
                ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('evaluation/figures/figure_3_faithfulness.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ Created Figure 3: Faithfulness Scores")

# Figure 4: Answer Quality Scores
def create_figure_4():
    fig, ax = plt.subplots(figsize=(8, 6))
    bars = ax.bar(models, answer_quality_scores, color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)
    ax.set_ylabel('Answer Quality Score', fontsize=12, fontweight='bold')
    ax.set_xlabel('Model', fontsize=12, fontweight='bold')
    ax.set_title('Answer Quality Scores by Model', fontsize=14, fontweight='bold', pad=20)
    ax.set_ylim(0, 5)
    ax.set_yticks(np.arange(0, 5.5, 0.5))
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    # Add value labels on bars
    for i, (bar, score) in enumerate(zip(bars, answer_quality_scores)):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.05,
                f'{score:.2f}',
                ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('evaluation/figures/figure_4_answer_quality.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ Created Figure 4: Answer Quality Scores")

# Figure 5: Average Response Time
def create_figure_5():
    fig, ax = plt.subplots(figsize=(8, 6))
    bars = ax.bar(models, response_times, color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)
    ax.set_ylabel('Average Response Time (seconds)', fontsize=12, fontweight='bold')
    ax.set_xlabel('Model', fontsize=12, fontweight='bold')
    ax.set_title('Average Response Time by Model', fontsize=14, fontweight='bold', pad=20)
    ax.set_ylim(0, 12)
    ax.set_yticks(np.arange(0, 13, 1))
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    # Add value labels on bars
    for i, (bar, time) in enumerate(zip(bars, response_times)):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.2,
                f'{time:.2f}s',
                ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('evaluation/figures/figure_5_response_time.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ Created Figure 5: Average Response Time")

# Figure 1: System Architecture Diagram
def create_figure_1():
    fig, ax = plt.subplots(figsize=(14, 10))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # Define box positions and sizes
    boxes = {
        'PDF Upload': (1, 8.5, 1.5, 0.8),
        'PDF Parser': (1, 7, 1.5, 0.8),
        'Text Chunks': (1, 5.5, 1.5, 0.8),
        'Embedding Model': (3.5, 5.5, 1.5, 0.8),
        'Vector Store\n(ChromaDB)': (6, 5.5, 1.5, 0.8),
        'User Query': (8.5, 8.5, 1.5, 0.8),
        'Query Embedding': (8.5, 7, 1.5, 0.8),
        'Retrieval': (6, 7, 1.5, 0.8),
        'RAG System': (3.5, 3, 1.5, 0.8),
        'LLM': (6, 3, 1.5, 0.8),
        'Answer + Citations': (3.5, 1.5, 1.5, 0.8),
        'Question Generator': (6, 1.5, 1.5, 0.8),
        'Web Interface': (8.5, 1.5, 1.5, 0.8),
    }
    
    # Draw boxes
    for name, (x, y, w, h) in boxes.items():
        box = FancyBboxPatch((x-w/2, y-h/2), w, h,
                            boxstyle="round,pad=0.1",
                            edgecolor='black',
                            facecolor='lightblue',
                            linewidth=1.5,
                            zorder=2)
        ax.add_patch(box)
        ax.text(x, y, name, ha='center', va='center', 
                fontsize=9, fontweight='bold', zorder=3)
    
    # Draw arrows
    arrows = [
        ((1, 8.1), (1, 7.4)),  # PDF Upload -> PDF Parser
        ((1, 6.6), (1, 5.9)),  # PDF Parser -> Text Chunks
        ((1.75, 5.5), (2.75, 5.5)),  # Text Chunks -> Embedding Model
        ((4.25, 5.5), (5.25, 5.5)),  # Embedding Model -> Vector Store
        ((8.5, 8.1), (8.5, 7.4)),  # User Query -> Query Embedding
        ((8.5, 6.6), (7.25, 7)),  # Query Embedding -> Retrieval
        ((6, 6.6), (6, 5.9)),  # Retrieval -> Vector Store (up)
        ((6.75, 5.5), (5.25, 3.4)),  # Vector Store -> RAG System
        ((3.5, 2.6), (3.5, 1.9)),  # RAG System -> Answer
        ((5, 3), (5.25, 3)),  # RAG System -> LLM
        ((6, 2.6), (6, 1.9)),  # LLM -> Question Generator
        ((5, 1.5), (4.25, 1.5)),  # Question Generator -> Answer
        ((5, 1.5), (7.25, 1.5)),  # Answer -> Web Interface
    ]
    
    for (start, end) in arrows:
        arrow = FancyArrowPatch(start, end,
                               arrowstyle='->',
                               mutation_scale=20,
                               linewidth=1.5,
                               color='darkblue',
                               zorder=1)
        ax.add_patch(arrow)
    
    ax.set_title('System Architecture Diagram', fontsize=16, fontweight='bold', pad=20)
    
    plt.tight_layout()
    plt.savefig('evaluation/figures/figure_1_system_architecture.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ Created Figure 1: System Architecture Diagram")

# Create figures directory
import os
os.makedirs('evaluation/figures', exist_ok=True)

# Generate all figures
print("Generating figures for the project report...")
print("=" * 60)
create_figure_1()
create_figure_2()
create_figure_3()
create_figure_4()
create_figure_5()
print("=" * 60)
print("All figures generated successfully!")
print("Figures saved in: evaluation/figures/")

