#!/usr/bin/env python3
"""
Terraria AI Agent - Main Entry Point

An AI that plays Terraria autonomously, capable of:
- Building NPC houses
- Mining blocks (stone, dirt, ores)
- Fighting zombies and Eye of Cthulhu
- Navigating the world
- Managing inventory

Usage:
    python main.py                    # Run with default settings
    python main.py --mode interactive # Run in interactive mode
    python main.py --mode demo        # Run demo mode
    python main.py --config config.yaml  # Use custom config

Requirements:
    - Terraria running in windowed mode at 1920x1080
    - Python 3.8+
    - Dependencies from requirements.txt

Author: Terraria AI Agent
"""

import argparse
import sys
import time
import signal
from typing import Optional

from terraria_ai import TerrariaAI
from terraria_ai.ai_agent import AIGoal, AITask


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Terraria AI Agent - Autonomous Terraria Player',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python main.py                          # Start the AI
    python main.py --mode interactive       # Interactive command mode
    python main.py --mode build             # Build houses mode
    python main.py --mode mine              # Mining mode
    python main.py --mode combat            # Combat training mode
    python main.py --goal boss              # Fight Eye of Cthulhu
        """
    )

    parser.add_argument(
        '--mode', '-m',
        choices=['auto', 'interactive', 'build', 'mine', 'combat', 'demo'],
        default='auto',
        help='Operating mode (default: auto)'
    )

    parser.add_argument(
        '--goal', '-g',
        choices=['idle', 'explore', 'gather', 'build', 'mine', 'fight', 'boss'],
        default=None,
        help='Initial goal to pursue'
    )

    parser.add_argument(
        '--config', '-c',
        type=str,
        default=None,
        help='Path to configuration file'
    )

    parser.add_argument(
        '--duration', '-d',
        type=int,
        default=None,
        help='Run duration in seconds (default: indefinite)'
    )

    parser.add_argument(
        '--hotbar',
        type=str,
        default=None,
        help='Hotbar configuration: pickaxe,sword,ranged,building,torch (slot numbers)'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )

    return parser.parse_args()


def setup_signal_handlers(ai: TerrariaAI):
    """Set up signal handlers for graceful shutdown."""
    def signal_handler(sig, frame):
        print("\nShutting down gracefully...")
        ai.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


def goal_from_string(goal_str: str) -> AIGoal:
    """Convert string to AIGoal enum."""
    mapping = {
        'idle': AIGoal.IDLE,
        'explore': AIGoal.EXPLORE,
        'gather': AIGoal.GATHER_RESOURCES,
        'build': AIGoal.BUILD_HOUSE,
        'mine': AIGoal.MINE,
        'fight': AIGoal.FIGHT,
        'boss': AIGoal.BOSS_FIGHT,
    }
    return mapping.get(goal_str, AIGoal.IDLE)


def interactive_mode(ai: TerrariaAI):
    """Run in interactive command mode."""
    print("""
╔═══════════════════════════════════════════════════════════╗
║           Terraria AI Agent - Interactive Mode             ║
╠═══════════════════════════════════════════════════════════╣
║ Commands:                                                  ║
║   build    - Build an NPC house                           ║
║   mine     - Start mining                                 ║
║   fight    - Engage combat                                ║
║   boss     - Fight Eye of Cthulhu (night only)            ║
║   explore  - Explore the world                            ║
║   status   - Show current status                          ║
║   stop     - Stop current action                          ║
║   quit     - Exit the program                             ║
╚═══════════════════════════════════════════════════════════╝
    """)

    while True:
        try:
            cmd = input("\n> ").strip().lower()

            if cmd == 'quit' or cmd == 'exit':
                break
            elif cmd == 'build':
                print("Starting house building...")
                ai.build_house()
            elif cmd == 'mine':
                print("Starting mining...")
                ai.set_goal(AIGoal.MINE)
            elif cmd == 'fight':
                print("Engaging combat...")
                ai.fight_enemies()
            elif cmd == 'boss':
                print("Summoning Eye of Cthulhu...")
                ai.summon_eye_of_cthulhu()
            elif cmd == 'explore':
                print("Exploring...")
                ai.explore()
            elif cmd == 'status':
                print(ai.get_status())
            elif cmd == 'stop':
                print("Stopping current action...")
                ai.set_goal(AIGoal.IDLE)
            elif cmd == 'help':
                print("Commands: build, mine, fight, boss, explore, status, stop, quit")
            else:
                print(f"Unknown command: {cmd}")
                print("Type 'help' for available commands")

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")

    ai.stop()


def build_mode(ai: TerrariaAI, count: int = 3):
    """Run in house building mode."""
    print(f"Building {count} NPC houses...")

    for i in range(count):
        print(f"Building house {i+1}/{count}...")
        ai.build_house()

        # Wait for completion
        while ai.current_goal == AIGoal.BUILD_HOUSE:
            time.sleep(0.5)

        print(f"House {i+1} complete!")

    print("All houses built!")


def mine_mode(ai: TerrariaAI, duration: int = 300):
    """Run in mining mode."""
    print(f"Mining for {duration} seconds...")

    ai.set_goal(AIGoal.MINE)
    start_time = time.time()

    while time.time() - start_time < duration:
        time.sleep(1)
        stats = ai.get_stats()
        print(f"Blocks mined: {stats['blocks_mined']}", end='\r')

    ai.set_goal(AIGoal.IDLE)
    print(f"\nMining complete! Total blocks: {ai.get_stats()['blocks_mined']}")


def combat_mode(ai: TerrariaAI, duration: int = 300):
    """Run in combat training mode."""
    print(f"Combat training for {duration} seconds...")
    print("Waiting for night time for zombies to spawn...")

    ai.set_goal(AIGoal.FIGHT)
    start_time = time.time()

    while time.time() - start_time < duration:
        time.sleep(1)
        stats = ai.get_stats()
        print(f"Enemies killed: {stats['enemies_killed']} | "
              f"Health: {stats['health']*100:.0f}%", end='\r')

    ai.set_goal(AIGoal.IDLE)
    print(f"\nCombat training complete! Total kills: {ai.get_stats()['enemies_killed']}")


def demo_mode(ai: TerrariaAI):
    """Run a demonstration of AI capabilities."""
    print("""
╔═══════════════════════════════════════════════════════════╗
║              Terraria AI Agent - Demo Mode                 ║
╠═══════════════════════════════════════════════════════════╣
║ This demo will showcase the AI's capabilities:             ║
║   1. Explore the area                                      ║
║   2. Mine some blocks                                      ║
║   3. Build an NPC house                                    ║
║   4. Fight any enemies encountered                         ║
╚═══════════════════════════════════════════════════════════╝
    """)

    input("Press Enter to start the demo...")

    # Phase 1: Explore
    print("\n[Phase 1] Exploring the area...")
    ai.set_goal(AIGoal.EXPLORE)
    time.sleep(10)

    # Phase 2: Mine
    print("\n[Phase 2] Mining blocks...")
    ai.set_goal(AIGoal.MINE)
    time.sleep(15)
    print(f"Blocks mined: {ai.get_stats()['blocks_mined']}")

    # Phase 3: Build
    print("\n[Phase 3] Building an NPC house...")
    ai.build_house()
    while ai.current_goal == AIGoal.BUILD_HOUSE:
        time.sleep(0.5)
    print(f"Houses built: {ai.get_stats()['houses_built']}")

    # Phase 4: Combat (if enemies present)
    print("\n[Phase 4] Ready for combat...")
    ai.set_goal(AIGoal.FIGHT)
    time.sleep(10)
    print(f"Enemies killed: {ai.get_stats()['enemies_killed']}")

    print("\n" + "="*60)
    print("Demo complete!")
    print(ai.get_status())


def main():
    """Main entry point."""
    args = parse_args()

    print("""
    ╔════════════════════════════════════════════════════════════════╗
    ║                                                                ║
    ║     ████████╗███████╗██████╗ ██████╗  █████╗ ██████╗ ██╗ █████╗   ║
    ║     ╚══██╔══╝██╔════╝██╔══██╗██╔══██╗██╔══██╗██╔══██╗██║██╔══██╗  ║
    ║        ██║   █████╗  ██████╔╝██████╔╝███████║██████╔╝██║███████║  ║
    ║        ██║   ██╔══╝  ██╔══██╗██╔══██╗██╔══██║██╔══██╗██║██╔══██║  ║
    ║        ██║   ███████╗██║  ██║██║  ██║██║  ██║██║  ██║██║██║  ██║  ║
    ║        ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝╚═╝  ╚═╝  ║
    ║                     █████╗ ██╗                                     ║
    ║                    ██╔══██╗██║                                     ║
    ║                    ███████║██║                                     ║
    ║                    ██╔══██║██║                                     ║
    ║                    ██║  ██║██║                                     ║
    ║                    ╚═╝  ╚═╝╚═╝                                     ║
    ║                                                                    ║
    ║                  Autonomous Terraria Player                        ║
    ║                                                                    ║
    ╚════════════════════════════════════════════════════════════════════╝
    """)

    print("Initializing AI Agent...")
    print("Make sure Terraria is running in windowed mode at 1920x1080")
    print()

    # Create AI instance
    ai = TerrariaAI(config_path=args.config)

    # Set up signal handlers
    setup_signal_handlers(ai)

    # Configure hotbar if specified
    if args.hotbar:
        slots = [int(x) for x in args.hotbar.split(',')]
        if len(slots) >= 5:
            ai.configure_hotbar(
                pickaxe=slots[0],
                sword=slots[1],
                ranged=slots[2],
                building=slots[3],
                torch=slots[4]
            )
            print(f"Hotbar configured: {slots}")

    # Set initial goal if specified
    if args.goal:
        ai.set_goal(goal_from_string(args.goal))

    # Run in selected mode
    try:
        if args.mode == 'interactive':
            interactive_mode(ai)
        elif args.mode == 'build':
            build_mode(ai)
        elif args.mode == 'mine':
            mine_mode(ai, args.duration or 300)
        elif args.mode == 'combat':
            combat_mode(ai, args.duration or 300)
        elif args.mode == 'demo':
            demo_mode(ai)
        else:  # auto mode
            print("Starting in automatic mode...")
            print("Press Ctrl+C to stop")
            print()

            if args.duration:
                # Run for specified duration
                start_time = time.time()
                ai.running = True

                while time.time() - start_time < args.duration:
                    ai._main_loop()
            else:
                # Run indefinitely
                ai.start()

    except KeyboardInterrupt:
        print("\nInterrupted by user")
    except Exception as e:
        print(f"Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
    finally:
        ai.cleanup()
        print("Goodbye!")


if __name__ == '__main__':
    main()
