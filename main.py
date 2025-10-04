import random
import pygame
import sys
import time
from typing import Dict, Any, Optional

from config import SimulationConfig, parse_args
from game.world import World
from game.agents.prey import Prey
from game.agents.plant import Plant
from game.agents.predator import Predator
from game.utils import generate_random_color
from game.ui import SimulationUI
from game.error_handler import error_handler


# This function has been removed as it's not used in the main simulation
# If needed, it's available in the analysis module


# Constants are now defined in SimulationConfig

def spawn_prey(world: World, count: int, config: SimulationConfig) -> None:
    """Spawn prey agents in the world.
    
    Args:
        world: The game world to spawn prey in
        count: Number of prey to spawn
        config: Simulation configuration
    """
    for _ in range(count):
        try:
            x = random.randint(config.prey_radius, config.width - config.prey_radius)
            y = random.randint(config.prey_radius, config.height - config.prey_radius)
            angle = random.uniform(0, 2 * 3.14159)  # 2 * pi
            color = generate_random_color()
            
            prey = Prey(
                x=x,
                y=y,
                speed=config.prey_speed,
                angle=angle,
                vision_range=config.prey_vision_range,
                vision_angle=config.prey_vision_angle,
                color=color,
                radius=config.prey_radius
            )
            world.add_agent(prey)
        except Exception as e:
            error_handler.log_error(f"Failed to spawn prey: {e}")

class SimulationRunner:
    """Main simulation runner class."""
    
    def __init__(self, config: SimulationConfig):
        """Initialize the simulation with configuration."""
        self.config = config
        self.running = True
        self.clock = pygame.time.Clock()
        
        # Initialize pygame and create window
        pygame.init()
        self.screen = pygame.display.set_mode((config.total_width, config.height))
        pygame.display.set_caption("Predator-Prey Simulation")
        
        # Create world and UI
        self.world = World(width=config.width, height=config.height, background_color=config.background_color)
        self.ui = SimulationUI(
            width=config.total_width,
            height=config.height,
            world=self.world,  # Pass the world reference
            ui_panel_width=config.ui_panel_width
        )
        
        # Spawn initial agents
        self.spawn_initial_agents()
    
    def handle_events(self) -> bool:
        """Handle pygame events.
        
        Returns:
            bool: True if the simulation should continue, False if it should stop
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            # Handle UI events if available
            if hasattr(self, 'ui') and self.ui and hasattr(self.ui, 'handle_input'):
                self.ui.handle_input(event)
                
        return True
    
    def spawn_initial_agents(self):
        """Spawn the initial agents (prey, plants, and predators)."""
        # Spawn prey
        spawn_prey(self.world, self.config.num_prey, self.config)
        
        # Spawn plants
        for _ in range(self.config.num_plants):
            x = random.randint(0, self.config.width)
            y = random.randint(0, self.config.height)
            self.world.add_agent(Plant(
                x=x,
                y=y,
                radius=self.config.plant_radius,
                energy=self.config.plant_energy
            ))
        
        # Spawn predators if enabled
        if self.config.num_predators > 0:
            for _ in range(self.config.num_predators):
                x = random.randint(0, self.config.width)
                y = random.randint(0, self.config.height)
                angle = random.uniform(0, 2 * 3.14159)
                predator = Predator(
                    x=x,
                    y=y,
                    radius=self.config.predator_radius,
                    speed=self.config.predator_speed,
                    angle=angle,
                    vision_range=self.config.predator_vision_range,
                    vision_angle=self.config.predator_vision_angle,
                    energy=self.config.predator_energy
                )
                self.world.add_agent(predator)

    def spawn_plants(self, count: int) -> None:
        """Spawn plant agents in the world.
        
        Args:
            count: Number of plants to spawn
        """
        for _ in range(count):
            x = random.randint(0, self.config.width)
            y = random.randint(0, self.config.height)
            self.world.add_agent(Plant(
                x=x,
                y=y,
                radius=self.config.plant_radius,
                energy=self.config.plant_energy
            ))
    
    def spawn_predators(self, count: int) -> None:
        """Spawn predator agents in the world.
        
        Args:
            count: Number of predators to spawn
        """
        for _ in range(count):
            x = random.randint(0, self.config.width)
            y = random.randint(0, self.config.height)
            angle = random.uniform(0, 2 * 3.14159)
            predator = Predator(
                x=x,
                y=y,
                radius=self.config.predator_radius,
                speed=self.config.predator_speed,
                angle=angle,
                vision_range=self.config.predator_vision_range,
                vision_angle=self.config.predator_vision_angle,
                energy=self.config.predator_energy
            )
            self.world.add_agent(predator)
    
    def update(self, dt: float) -> None:
        """Update the simulation state.
        
        Args:
            dt: Time delta since last update in seconds
        """
        # Update the world state
        self.world.update(dt)
        
        # Update UI if needed
        if hasattr(self, 'ui') and self.ui:
            # Update any UI-specific state here
            pass
    
    def render(self) -> None:
        """Render the current state of the simulation."""
        # Clear the screen with the background color
        if hasattr(self, 'world') and hasattr(self.world, 'background_color'):
            self.screen.fill(self.world.background_color)
        else:
            self.screen.fill((0, 0, 0))  # Black fallback
        
        # Draw the world
        if hasattr(self, 'world') and hasattr(self.world, 'draw'):
            self.world.draw(self.screen)
        
        # Draw the UI
        if hasattr(self, 'ui') and self.ui and hasattr(self.ui, 'draw'):
            # Get the required data for the UI
            prey_count = len([a for a in self.world.agents if isinstance(a, Prey)]) if hasattr(self.world, 'agents') else 0
            plant_count = len([a for a in self.world.agents if isinstance(a, Plant)]) if hasattr(self.world, 'agents') else 0
            fps = int(self.clock.get_fps()) if hasattr(self, 'clock') else 0
            total_width = self.config.total_width if hasattr(self.config, 'total_width') else 800
            
            # Update the UI with the current state
            if hasattr(self.ui, 'update'):
                predator_count = len([a for a in self.world.agents if hasattr(a, 'predator')]) if hasattr(self.world, 'agents') else 0
                self.ui.update(1.0 / 60.0, prey_count, plant_count, predator_count)
            
            # Draw the UI with the required arguments
            self.ui.draw(self.screen, prey_count, plant_count, fps, total_width)
        
        # Update the display
        pygame.display.flip()
    
    def run(self) -> None:
        """Run the main simulation loop."""
        self.running = True
        last_time = time.time()
        
        while self.running:
            # Calculate delta time
            current_time = time.time()
            dt = current_time - last_time
            last_time = current_time
            
            # Cap delta time to avoid physics issues
            dt = min(dt, 0.1)
            
            # Handle events
            self.running = self.handle_events()
            
            # Update simulation
            self.update(dt)
            
            # Render
            self.render()
            
            # Cap the frame rate
            self.clock.tick(self.config.fps)

def run_simulation():
    """Run the simulation with error handling."""
    try:
        # Parse command line arguments and create config
        args = parse_args()
        config = SimulationConfig.from_args(args)
        
        # Set random seed if specified
        if config.seed is not None:
            random.seed(config.seed)
            
        # Initialize and run the simulation
        runner = SimulationRunner(config)
        return runner.run()
        
    except Exception as e:
        error_handler.handle_error(e)
        error_handler.handle_error(e, {
            'context': 'Simulation runtime error',
            'error_type': type(e).__name__
        })
    finally:
        pygame.quit()
        return 0
        return 1

def main():
    """Entry point with error handling wrapper."""
    try:
        return run_simulation()
    except Exception as e:
        error_handler.handle_error(e, {
            'context': 'Unhandled exception in main',
            'exception_type': type(e).__name__
        })
        return 1

if __name__ == "__main__":
    sys.exit(main())
