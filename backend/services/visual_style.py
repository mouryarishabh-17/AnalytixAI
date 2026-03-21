
import matplotlib.pyplot as plt
from cycler import cycler

def apply_modern_theme():
    """
    Applies a modern, dark-mode fintech aesthetic to Matplotlib charts.
    """
    # Colors
    bg_color = '#1e1e2f'        # Dark Navy Background
    plot_bg_color = '#1e1e2f'   # Plot Area Background (Same as figure for seamless look)
    text_color = '#e0e0e0'      # Off-white text
    grid_color = '#33334d'      # Subtle purple-gray grid
    accent_color = '#00f2ea'    # Neon Cyan

    # Neon Color Cycle
    neon_cycle = [
        '#00f2ea',  # Neon Cyan
        '#ff00ff',  # Neon Magenta
        '#39ff14',  # Neon Lime
        '#ffd700',  # Gold
        '#ff4500',  # Orange Red
        '#1e90ff',  # Dodger Blue
    ]

    # Update global params
    plt.rcParams.update({
        # Backgrounds
        'figure.facecolor': bg_color,
        'axes.facecolor': plot_bg_color,
        'savefig.facecolor': bg_color,

        # Text
        'text.color': text_color,
        'axes.labelcolor': text_color,
        'xtick.color': text_color,
        'ytick.color': text_color,
        'axes.titlecolor': 'white',
        'axes.titlesize': 14,
        'axes.titleweight': 'bold',
        'axes.labelsize': 10,
        
        # Grid
        'axes.grid': True,
        'grid.color': grid_color,
        'grid.linestyle': '--',
        'grid.linewidth': 0.8,
        'grid.alpha': 0.5,

        # Spines (Borders)
        'axes.spines.top': False,
        'axes.spines.right': False,
        'axes.spines.bottom': True,
        'axes.spines.left': True,
        'axes.edgecolor': grid_color,

        # Colors
        'axes.prop_cycle': cycler(color=neon_cycle),
        
        # Font
        'font.family': 'sans-serif',
        'font.sans-serif': ['Arial', 'Helvetica', 'DejaVu Sans'],
    })

def basic_bar_chart(df, cat_col, amt_col, title, filename):
    try:
        apply_modern_theme()
        plt.figure(figsize=(10, 6))
        
        # Data
        data = df.groupby(cat_col)[amt_col].sum().sort_values(ascending=False).head(10)
        
        # Plot
        bars = plt.bar(data.index, data.values, color='#00f2ea', alpha=0.8, edgecolor='#00f2ea', linewidth=1)
        
        # Add values on top
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                     f'{int(height)}',
                     ha='center', va='bottom', color='white', fontsize=8)

        plt.title(title.upper())
        plt.xlabel(cat_col.title())
        plt.ylabel(amt_col.title())
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        path = f"charts/{filename}.png"
        plt.savefig(path, dpi=120)
        plt.close()
        return path
    except Exception as e:
        print(f"Chart Error ({title}): {e}")
        plt.close()
        return None

def basic_line_chart(df, date_col, amt_col, title, filename):
    try:
        apply_modern_theme()
        plt.figure(figsize=(10, 6))
        
        # Data Processing
        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
        df_sorted = df.dropna(subset=[date_col]).sort_values(date_col)
        
        if df_sorted.empty: return None

        # Plot
        plt.plot(df_sorted[date_col], df_sorted[amt_col], 
                 marker='o', markersize=4, linestyle='-', linewidth=2, 
                 color='#ff00ff', alpha=0.9) # Neon Magenta
        
        # Fill area under curve for "premium" look
        plt.fill_between(df_sorted[date_col], df_sorted[amt_col], color='#ff00ff', alpha=0.1)

        plt.title(title.upper())
        plt.xlabel('Date')
        plt.ylabel(amt_col.title())
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        path = f"charts/{filename}.png"
        plt.savefig(path, dpi=120)
        plt.close()
        return path
    except Exception as e:
        print(f"Chart Error ({title}): {e}")
        plt.close()
        return None
