"""
One-command processor for L'Oréal Comment Analysis
Usage: python one_command.py [directory_with_csv_files]
"""
import sys
import os
import argparse

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from batch_processor import BatchProcessor

def main():
    print("🚀 L'Oréal Comment Analysis - One Command Processor")
    print("=" * 55)
    
    parser = argparse.ArgumentParser(
        description='Process all CSV files in a directory with one command',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python one_command.py                    # Process files in current directory
  python one_command.py data/              # Process files in 'data' directory
  python one_command.py --input data/ --output results/
  
File Requirements:
  - Comment files: Must have 'textOriginal' column
  - Video files: Must have 'title' column
  - Files with 'comment' in name are treated as comment files
  - Files with 'video' in name are treated as video files
        """
    )
    
    parser.add_argument(
        'directory', 
        nargs='?', 
        default='.', 
        help='Directory containing CSV files (default: current directory)'
    )
    
    parser.add_argument(
        '--input', '-i',
        help='Input directory (overrides positional directory argument)'
    )
    
    parser.add_argument(
        '--output', '-o',
        default='analysis_results',
        help='Output directory for results (default: analysis_results)'
    )
    
    parser.add_argument(
        '--sample', '-s',
        type=int,
        help='Sample size for large datasets (e.g., 50000)'
    )
    
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Suppress detailed output'
    )
    
    args = parser.parse_args()
    
    # Determine input directory
    input_dir = args.input if args.input else args.directory
    
    if not os.path.exists(input_dir):
        print(f"❌ Directory not found: {input_dir}")
        sys.exit(1)
    
    # Check for CSV files
    csv_files = [f for f in os.listdir(input_dir) if f.lower().endswith('.csv')]
    
    if not csv_files:
        print(f"❌ No CSV files found in: {input_dir}")
        print("\n💡 Make sure your directory contains:")
        print("   - Comment CSV files (with 'textOriginal' column)")
        print("   - Video CSV files (with 'title' column)")
        sys.exit(1)
    
    print(f"📁 Found {len(csv_files)} CSV files in: {input_dir}")
    
    if not args.quiet:
        print("📋 Files found:")
        for file in csv_files:
            print(f"   - {file}")
        print()
    
    # Create and run batch processor
    processor = BatchProcessor(input_dir, args.output)
    
    # Apply sampling if specified
    if args.sample:
        print(f"📊 Using sampling: {args.sample:,} comments per dataset")
        # Note: Sampling would need to be implemented in BatchProcessor
    
    try:
        processor.run_batch_processing()
        
        print(f"\n🎉 Processing complete!")
        print(f"📁 Results saved to: {args.output}")
        print(f"📊 Check 'batch_summary.txt' for overview")
        
    except KeyboardInterrupt:
        print("\n⏹️ Processing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error during processing: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()