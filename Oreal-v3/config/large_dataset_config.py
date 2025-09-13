"""
Configuration optimized for large datasets (50k+ comments)
"""

# Performance optimizations for large datasets
LARGE_DATASET_CONFIG = {
    'batch_sizes': {
        'small': 250,      # < 10k comments
        'medium': 500,     # 10k - 50k comments  
        'large': 1000,     # 50k - 100k comments
        'xlarge': 2000     # > 100k comments
    },
    
    'sampling': {
        'language_detection_sample': 5000,  # Sample size for language detection
        'topic_extraction_sample': 10000,   # Sample size for topic extraction
        'enable_sampling_above': 100000     # Enable sampling above this threshold
    },
    
    'processing': {
        'use_textblob_threshold': 1000,     # Only use TextBlob for batches smaller than this
        'memory_efficient_mode': True,      # Enable memory optimizations
        'progress_update_frequency': 100,   # Update progress every N batches
        'chunk_size_for_export': 10000     # Export in chunks for large datasets
    },
    
    'ui_optimizations': {
        'max_preview_rows': 1000,           # Limit preview rows in UI
        'default_sample_size': 50000,       # Default sample for very large datasets
        'enable_pagination': True,          # Enable pagination for large results
        'lazy_loading': True               # Load visualizations on demand
    }
}

# Memory management
MEMORY_CONFIG = {
    'cleanup_intermediate_results': True,   # Clean up temporary DataFrames
    'use_categorical_dtypes': True,         # Use categorical for repeated strings
    'optimize_dtypes': True,                # Optimize numeric dtypes
    'garbage_collect_frequency': 1000       # Run garbage collection every N operations
}

# Visualization settings for large datasets
VIZ_CONFIG_LARGE = {
    'max_points_scatter': 10000,           # Limit scatter plot points
    'sample_for_viz': True,                # Sample data for visualizations
    'use_plotly_webgl': True,              # Use WebGL for better performance
    'disable_animations': True,            # Disable animations for speed
    'chart_height': 400,                   # Smaller charts for better performance
    'max_categories_pie': 10               # Limit pie chart categories
}

# Export optimizations
EXPORT_CONFIG_LARGE = {
    'chunk_export': True,                  # Export in chunks
    'compress_csv': True,                  # Compress CSV exports
    'limit_export_rows': 1000000,          # Maximum rows per export
    'include_sample_in_report': True,      # Include sample analysis in reports
    'generate_summary_only': False        # Option to generate summary only
}

def get_optimal_batch_size(dataset_size):
    """Get optimal batch size based on dataset size"""
    config = LARGE_DATASET_CONFIG['batch_sizes']
    
    if dataset_size < 10000:
        return config['small']
    elif dataset_size < 50000:
        return config['medium']
    elif dataset_size < 100000:
        return config['large']
    else:
        return config['xlarge']

def should_use_sampling(dataset_size):
    """Determine if sampling should be used"""
    return dataset_size > LARGE_DATASET_CONFIG['sampling']['enable_sampling_above']

def get_recommended_sample_size(dataset_size):
    """Get recommended sample size for very large datasets"""
    if dataset_size <= 50000:
        return dataset_size
    elif dataset_size <= 100000:
        return 50000
    elif dataset_size <= 500000:
        return 75000
    else:
        return 100000

def optimize_dataframe_memory(df):
    """Optimize DataFrame memory usage"""
    if not MEMORY_CONFIG['optimize_dtypes']:
        return df
    
    # Convert object columns to category where appropriate
    for col in df.select_dtypes(include=['object']).columns:
        if df[col].nunique() / len(df) < 0.5:  # Less than 50% unique values
            df[col] = df[col].astype('category')
    
    # Optimize numeric columns
    for col in df.select_dtypes(include=['int64']).columns:
        if df[col].min() >= 0 and df[col].max() <= 255:
            df[col] = df[col].astype('uint8')
        elif df[col].min() >= -128 and df[col].max() <= 127:
            df[col] = df[col].astype('int8')
        elif df[col].min() >= 0 and df[col].max() <= 65535:
            df[col] = df[col].astype('uint16')
        elif df[col].min() >= -32768 and df[col].max() <= 32767:
            df[col] = df[col].astype('int16')
    
    return df

# Performance monitoring
PERFORMANCE_CONFIG = {
    'track_memory_usage': True,
    'track_processing_time': True,
    'log_batch_progress': True,
    'warn_on_slow_processing': True,
    'memory_warning_threshold': 0.8  # Warn when using 80% of available memory
}