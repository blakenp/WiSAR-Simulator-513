import argparse
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.patches as mpatches
import pandas as pd
from tqdm import tqdm
from matplotlib.collections import LineCollection

# --- Visual config ---
HAZARD_STYLES = {
    "standing_water": {"color": "#244d60", "alpha": 0.4, "zorder": 1},
    "running_water": {"color": "#4a90d9", "alpha": 0.4, "zorder": 1},
    "tree":  {"color": "#4a7c3f", "alpha": 0.6, "zorder": 1},
    "undergrowth":  {"color": "#3e331b", "alpha": 0.6, "zorder": 1},
    "boulder":  {"color": "#3b4244", "alpha": 0.6, "zorder": 1},
}
HAZARD_DEFAULT_STYLE = {"color": "#aaaaaa", "alpha": 0.4, "zorder": 1}

AGENT_STYLE   = {"color": "#e74c3c", "marker": "^", "s": 80, "zorder": 4, "label": "Agent"}
TARGET_STYLE  = {"color": "#7134db", "marker": "o", "s": 60, "zorder": 4, "label": "Target"}
VORONOI_STYLE = {"color": "#3498db", "alpha": 0.15, "linewidth": 0.8, "zorder": 2}

def parse_args():
    parser = argparse.ArgumentParser(description="Animate Voronoi topological cloud.")
    parser.add_argument("--agents",  required=True, help="Path to agents CSV")
    parser.add_argument("--targets", required=True, help="Path to targets CSV")
    parser.add_argument("--hazards", required=True, help="Path to hazards CSV")
    parser.add_argument("--voronoi", required=True, help="Path to voronoi ridges CSV")
    parser.add_argument("--output",  default="voronoi_sim.gif", help="Output file (.gif)")
    parser.add_argument("--fps",     type=int, default=10, help="Frames per second")
    parser.add_argument("--interval",type=int, default=100, help="Delay between frames in ms")
    return parser.parse_args()

def draw_hazards(ax, hazards_df):
    for _, hazard in hazards_df.iterrows():
        style = HAZARD_STYLES.get(hazard.get("type", ""), HAZARD_DEFAULT_STYLE)
        rect = mpatches.Rectangle(
            (hazard["x"], hazard["y"]),
            hazard["x_size"], hazard["y_size"],
            color=style["color"], alpha=style["alpha"], zorder=style["zorder"],
        )
        ax.add_patch(rect)

def make_animate_fn(agents_df, targets_df, voronoi_df, ax, timesteps):
    agent_scatter  = ax.scatter([], [], **AGENT_STYLE)
    target_scatter = ax.scatter([], [], **TARGET_STYLE)
    
    # LineCollection is much faster than drawing individual lines per frame
    voronoi_lines = LineCollection([], **VORONOI_STYLE)
    ax.add_collection(voronoi_lines)
    
    timestamp_text = ax.text(0.02, 0.96, "", transform=ax.transAxes, fontsize=9, verticalalignment="top")

    def animate(timestep):
        a = agents_df[agents_df["timestep"] == timestep]
        t = targets_df[targets_df["timestep"] == timestep]
        v = voronoi_df[voronoi_df["timestep"] == timestep]

        # Redraw Agents and Targets
        agent_scatter.set_offsets(a[["x", "y"]].values)
        target_scatter.set_offsets(t[["x", "y"]].values)
        
        # Redraw Voronoi Ridges
        # v contains columns: x1, y1, x2, y2. Reshape to [[(x1,y1), (x2,y2)], ...]
        if not v.empty:
            segments = v[['x1', 'y1', 'x2', 'y2']].values.reshape(-1, 2, 2)
            voronoi_lines.set_segments(segments)
        else:
            voronoi_lines.set_segments([])

        timestamp_text.set_text(f"t = {timestep}")
        return agent_scatter, target_scatter, voronoi_lines, timestamp_text

    return animate

def main():
    args = parse_args()

    # Data loading
    base_path = "search_sim/finished_runs/"
    agents_df  = pd.read_csv(f"{base_path}{args.agents}")
    targets_df = pd.read_csv(f"{base_path}{args.targets}")
    hazards_df = pd.read_csv(f"{base_path}{args.hazards}")
    voronoi_df = pd.read_csv(f"{base_path}{args.voronoi}")

    timesteps = sorted(agents_df["timestep"].unique())
    
    # Calculate bounds
    all_x = pd.concat([agents_df["x"], hazards_df["x"]])
    all_y = pd.concat([agents_df["y"], hazards_df["y"]])
    padding = 5.0
    bounds = (all_x.min()-padding, all_x.max()+padding, all_y.min()-padding, all_y.max()+padding)

    fig, ax = plt.subplots(figsize=(8, 8))
    ax.set_xlim(bounds[0], bounds[1])
    ax.set_ylim(bounds[2], bounds[3])
    ax.set_aspect("equal")
    ax.set_title("Voronoi Belief Cloud Navigation")

    draw_hazards(ax, hazards_df)
    
    # Legend
    legend_elements = [
        mpatches.Patch(color=AGENT_STYLE["color"], label="Agent"),
        mpatches.Patch(color=TARGET_STYLE["color"], label="Target"),
        mpatches.Patch(color=VORONOI_STYLE["color"], alpha=0.6, label="Voronoi Belief Cloud"),
        mpatches.Patch(color="#3b4244", label="Static Hazards")
    ]
    ax.legend(handles=legend_elements, loc="upper right", fontsize=8)

    animate_fn = make_animate_fn(agents_df, targets_df, voronoi_df, ax, timesteps)

    ani = animation.FuncAnimation(
        fig, animate_fn, frames=tqdm(timesteps),
        interval=args.interval, blit=True
    )

    output_path = f"search_sim/animations/{args.output}"
    ani.save(output_path, writer="pillow", fps=args.fps)
    print(f"Saved Voronoi animation to {output_path}")

if __name__ == "__main__":
    main()