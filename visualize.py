import matplotlib.pyplot as plt
from pathlib import Path

def generate_timeline_chart(events, exposure_time, output_file='timeline.png'):
    """Generate exposure timeline visualization"""
    
    if not events or not exposure_time:
        print("[-] Cannot generate chart")
        return
    
    fig, ax = plt.subplots(figsize=(12, 5))
    
    times = [str(e['EventTime']) for e in events]
    names = [e['EventName'] for e in events]
    
    y_pos = range(len(times))
    colors = ['red' if 'Policy' in name else 'blue' for name in names]
    
    ax.barh(y_pos, [1]*len(times), color=colors, alpha=0.6)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(names, fontsize=9)
    ax.set_xlabel('Timeline')
    ax.set_title('BreachClock - Exposure Timeline', fontsize=12, fontweight='bold')
    
    plt.tight_layout()
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"[+] Chart saved to {output_file}")
