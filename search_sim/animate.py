import argparse
import math
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.patches as mpatches
import pandas as pd


# --- Visual config ---
HAZARD_STYLES = {
    "standing_water": {"color": "#244d60", "alpha": 0.4, "zorder": 1},
    "running_water": {"color": "#4a90d9", "alpha": 0.4, "zorder": 1},
    "tree":  {"color": "#4a7c3f", "alpha": 0.6, "zorder": 1},
    "undergrowth":  {"color": "#3e331b", "alpha": 0.6, "zorder": 1},
    "boulder":  {"color": "#3b4244", "alpha": 0.6, "zorder": 1},
}
HAZARD_DEFAULT_STYLE = {"color": "#aaaaaa", "alpha": 0.4, "zorder": 1}

AGENT_STYLE  = {"color": "#e74c3c", "marker": "^", "s": 80, "zorder": 3, "label": "Agent"}
TARGET_STYLE = {"color": "#7134db", "marker": "o", "s": 60, "zorder": 3, "label": "Target"}


def parse_args():
    parser = argparse.ArgumentParser(description="Animate a search and rescue simulation.")
    parser.add_argument("--agents",  required=True, help="Path to agents CSV")
    parser.add_argument("--targets", required=True, help="Path to targets CSV")
    parser.add_argument("--hazards", required=True, help="Path to hazards CSV")
    parser.add_argument("--output",  default="simulation.gif", help="Output file (.gif)")
    parser.add_argument("--fps",     type=int, default=10, help="Frames per second")
    parser.add_argument("--interval",type=int, default=100, help="Delay between frames in ms")
    return parser.parse_args()


def compute_bounds(agents_df, targets_df, hazards_df, padding=5.0):
    """Compute axis limits that fit all entities with some padding."""
    all_x = pd.concat([agents_df["x"], targets_df["x"], hazards_df["x"]])
    all_y = pd.concat([agents_df["y"], targets_df["y"], hazards_df["y"]])
    return (
        all_x.min() - padding, all_x.max() + padding,
        all_y.min() - padding, all_y.max() + padding,
    )


def draw_hazards(ax, hazards_df):
    """
    Draw hazards as circles. Called once since they are static.
    Returns the drawn artists so they can be kept across ax.clear() calls
    if needed, but since we draw them once before the animation loop
    and don't clear them, they persist automatically.
    """
    for _, hazard in hazards_df.iterrows():
        style = HAZARD_STYLES.get(hazard.get("type", ""), HAZARD_DEFAULT_STYLE)
        radius = hazard.get("radius", 1.0)
        circle = mpatches.Circle(
            (hazard["x"], hazard["y"]),
            radius=radius,
            color=style["color"],
            alpha=style["alpha"],
            zorder=style["zorder"],
        )
        ax.add_patch(circle)
        ax.text(
            hazard["x"], hazard["y"],
            hazard.get("type", ""),
            fontsize=6, ha="center", va="center",
            color="white", zorder=style["zorder"] + 1,
        )


def make_legend(ax):
    legend_elements = [
        mpatches.Patch(color=AGENT_STYLE["color"],  label="Agent"),
        mpatches.Patch(color=TARGET_STYLE["color"], label="Target"),
        mpatches.Patch(color=HAZARD_STYLES["standing_water"]["color"], alpha=0.6, label="Standing Water"),
        mpatches.Patch(color=HAZARD_STYLES["running_water"]["color"], alpha=0.6, label="Running Water"),
        mpatches.Patch(color=HAZARD_STYLES["tree"]["color"],  alpha=0.6, label="Tree"),
        mpatches.Patch(color=HAZARD_STYLES["undergrowth"]["color"],  alpha=0.6, label="Undergrowth"),
        mpatches.Patch(color=HAZARD_STYLES["boulder"]["color"],  alpha=0.6, label="Boulder"),
    ]
    ax.legend(handles=legend_elements, loc="upper right", fontsize=8)


def make_animate_fn(agents_df, targets_df, hazards_df, ax, bounds, timesteps):
    """
    Returns the per-frame update function for FuncAnimation.
    Agents and targets are redrawn each frame; hazards are static background.
    """
    # Scatter plot handles — created once, updated each frame for efficiency
    # (avoids clearing and redrawing the entire axes)
    agent_scatter  = ax.scatter([], [], **AGENT_STYLE)
    target_scatter = ax.scatter([], [], **TARGET_STYLE)
    timestamp_text = ax.text(
        0.02, 0.96, "", transform=ax.transAxes,
        fontsize=9, verticalalignment="top"
    )

    def animate(timestep):
        a = agents_df[agents_df["timestep"]  == timestep]
        t = targets_df[targets_df["timestep"] == timestep]

        agent_scatter.set_offsets(a[["x", "y"]].values)
        target_scatter.set_offsets(t[["x", "y"]].values)
        timestamp_text.set_text(f"t = {timestep}")

        return agent_scatter, target_scatter, timestamp_text

    return animate


def main():
    args = parse_args()

    agents = str(f"search_sim/finished_runs/{args.agents}")
    targets = str(f"search_sim/finished_runs/{args.targets}")
    hazards = str(f"search_sim/finished_runs/{args.hazards}")

    agents_df  = pd.read_csv(agents)
    targets_df = pd.read_csv(targets)
    hazards_df = pd.read_csv(hazards)

    timesteps = sorted(agents_df["timestep"].unique())
    bounds    = compute_bounds(agents_df, targets_df, hazards_df)

    fig, ax = plt.subplots(figsize=(8, 8))
    ax.set_xlim(bounds[0], bounds[1])
    ax.set_ylim(bounds[2], bounds[3])
    ax.set_aspect("equal")
    ax.set_title("Search and Rescue Simulation")
    ax.set_xlabel("x")
    ax.set_ylabel("y")

    # Hazards are drawn once here as a static background layer
    draw_hazards(ax, hazards_df)
    make_legend(ax)

    animate_fn = make_animate_fn(agents_df, targets_df, hazards_df, ax, bounds, timesteps)

    ani = animation.FuncAnimation(
        fig,
        animate_fn,
        frames=timesteps,
        interval=args.interval,
        blit=True,         # only redraw changed artists — much faster
    )

    output = str(f"search_sim/animations/{args.output}")

    ani.save(output, writer="pillow", fps=args.fps)

    print(f"Saved animation to {output}")


if __name__ == "__main__":
    main()