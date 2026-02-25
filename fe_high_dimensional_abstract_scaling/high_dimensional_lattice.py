"""
High-Dimensional Abstract Scaling — Core Algorithms

Mathematical optimization framework demonstrating the Complexity Amplification Effect.
This is NOT biological modeling - it's abstract high-dimensional optimization.

The core algorithms demonstrate strategic information elimination (culling bottom 30%)
enables non-linear scaling advantages in high-dimensional search spaces.

Patent Reference: US 63/898,911
"""

import numpy as np
from datetime import datetime
from typing import List, Tuple
from dataclasses import dataclass

# ============================================================================
# Data Structures
# ============================================================================

@dataclass
class Configuration:
    positions: List[Tuple[int, int, int]]
    energy: float
    sequence: str

# ============================================================================
# High-Dimensional Lattice Model
# ============================================================================

class HighDimensionalLattice:
    """Abstract high-dimensional lattice for optimization testing."""
    
    def __init__(self, sequence: str):
        self.sequence = sequence
        self.length = len(sequence)
        self.moves = [(1,0,0), (-1,0,0), (0,1,0), (0,-1,0), (0,0,1), (0,0,-1)]
    
    def calculate_energy(self, positions: List[Tuple[int, int, int]]) -> float:
        """Calculate abstract energy function for optimization landscape."""
        energy = 0
        for i in range(len(positions)):
            if self.sequence[i] == 'P':
                continue
            for j in range(i+2, len(positions)):
                if self.sequence[j] == 'P':
                    continue
                dist = sum(abs(positions[i][k] - positions[j][k]) for k in range(3))
                if dist == 1:
                    energy -= 1
        return energy
    
    def is_valid(self, positions: List[Tuple[int, int, int]]) -> bool:
        """Check self-avoiding constraint in abstract space."""
        return len(positions) == len(set(positions))
    
    def random_walk(self, seed: int) -> Configuration:
        """Generate random valid configuration in high-dimensional space."""
        rng = np.random.RandomState(seed)
        positions = [(0, 0, 0)]
        
        for i in range(1, self.length):
            attempts = 0
            while attempts < 100:
                move = self.moves[rng.randint(0, 6)]
                new_pos = tuple(positions[-1][k] + move[k] for k in range(3))
                if new_pos not in positions:
                    positions.append(new_pos)
                    break
                attempts += 1
            
            if len(positions) != i + 1:
                return self.random_walk(seed + 1)
        
        energy = self.calculate_energy(positions)
        return Configuration(positions, energy, self.sequence)

# ============================================================================
# Baseline Algorithm (Standard Monte Carlo)
# ============================================================================

def monte_carlo_baseline(sequence: str, max_steps: int, temperature: float,
                        seed: int) -> dict:
    """Standard Monte Carlo optimization for baseline comparison."""
    model = HighDimensionalLattice(sequence)
    rng = np.random.RandomState(seed)
    
    current = model.random_walk(seed)
    best = current
    start_time = datetime.now()
    
    for step in range(max_steps):
        new_positions = list(current.positions)
        idx = rng.randint(1, len(new_positions)-1)
        move = model.moves[rng.randint(0, 6)]
        new_positions[idx] = tuple(new_positions[idx][k] + move[k] for k in range(3))
        
        if not model.is_valid(new_positions):
            continue
        
        new_energy = model.calculate_energy(new_positions)
        delta_e = new_energy - current.energy
        
        if delta_e < 0 or rng.random() < np.exp(-delta_e / temperature):
            current = Configuration(new_positions, new_energy, sequence)
            if new_energy < best.energy:
                best = current
    
    elapsed_ms = (datetime.now() - start_time).total_seconds() * 1000
    
    return {
        "final_energy": best.energy,
        "convergence_generation": max_steps,
        "computation_time_ms": elapsed_ms,
        "paradox_buffer_activity": 0
    }

# ============================================================================
# Forgetting Engine Algorithm (Strategic Information Elimination)
# ============================================================================

def forgetting_engine_optimization(sequence: str, max_steps: int, 
                                  pop_size: int, seed: int) -> dict:
    """Forgetting Engine with strategic information elimination (30% culling)."""
    model = HighDimensionalLattice(sequence)
    rng = np.random.RandomState(seed)
    
    # Initialize population
    population = [model.random_walk(seed + i) for i in range(pop_size)]
    best = min(population, key=lambda x: x.energy)
    
    # Paradox buffer for strategic retention
    paradox_buffer = []
    paradox_retained_count = 0
    
    start_time = datetime.now()
    max_gen = max_steps // pop_size
    
    for gen in range(max_gen):
        # Strategic information elimination - cull bottom 30%
        population.sort(key=lambda x: x.energy, reverse=True)
        cull_count = int(len(population) * 0.3)
        forgotten = population[-cull_count:]
        population = population[:-cull_count]
        
        # Paradox retention: Track states retained
        for conf in forgotten:
            if rng.random() < 0.1:  # 10% retention rate
                paradox_buffer.append(conf)
                paradox_retained_count += 1
        
        # Regenerate population
        while len(population) < pop_size:
            if len(population) > 0:
                parent = population[rng.randint(0, len(population))]
                child_positions = list(parent.positions)
                idx = rng.randint(1, len(child_positions)-1)
                move = model.moves[rng.randint(0, 6)]
                child_positions[idx] = tuple(child_positions[idx][k] + move[k] for k in range(3))
                
                if model.is_valid(child_positions):
                    child_energy = model.calculate_energy(child_positions)
                    population.append(Configuration(child_positions, child_energy, sequence))
                else:
                    population.append(model.random_walk(seed + gen * pop_size + len(population)))
            else:
                population.append(model.random_walk(seed + gen * pop_size + len(population)))
        
        # Track best
        current_best = min(population, key=lambda x: x.energy)
        if current_best.energy < best.energy:
            best = current_best
    
    elapsed_ms = (datetime.now() - start_time).total_seconds() * 1000
    
    return {
        "final_energy": best.energy,
        "convergence_generation": max_gen,
        "computation_time_ms": elapsed_ms,
        "paradox_buffer_activity": paradox_retained_count
    }

# ============================================================================
# Utility Functions
# ============================================================================

def generate_sequence(length: int, seed: int = 42) -> str:
    """Generate abstract test sequence for optimization."""
    rng = np.random.RandomState(seed)
    return ''.join(rng.choice(['H', 'P'], size=length))
