"""
3D HP Lattice Protein Folding — Core Algorithms

Duplicated from validated study (FE-3D-PF-2025-10-27) in:
  CONEXUS_DATA_DUMP/DOMAIN DATA/protein_folding_3d/
  protein_folding_3d_forgetting_engine_validation_study.py

The HP3DLattice, monte_carlo_3d(), and forgetting_engine_3d() functions
are copied verbatim from the validated source. Only addition is
generate_sequence() for the multi-length scaling study.

Patent Reference: US 63/898,911
"""

import numpy as np
from dataclasses import dataclass
from typing import List, Tuple
from datetime import datetime


# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class Conformation3D:
    positions: List[Tuple[int, int, int]]
    energy: float
    sequence: str


# ============================================================================
# 3D HP LATTICE MODEL (verbatim from validated study)
# ============================================================================

class HP3DLattice:
    """3D HP lattice protein folding model."""

    def __init__(self, sequence: str):
        self.sequence = sequence
        self.length = len(sequence)
        self.moves = [(1,0,0), (-1,0,0), (0,1,0), (0,-1,0), (0,0,1), (0,0,-1)]

    def calculate_energy(self, positions: List[Tuple[int, int, int]]) -> float:
        """Calculate H-H contact energy."""
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
        """Check self-avoiding walk constraint."""
        return len(positions) == len(set(positions))

    def random_walk(self, seed: int) -> Conformation3D:
        """Generate random valid 3D conformation."""
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
        return Conformation3D(positions, energy, self.sequence)


# ============================================================================
# MONTE CARLO ALGORITHM (verbatim from validated study)
# ============================================================================

def monte_carlo_3d(sequence: str, max_steps: int, temperature: float,
                   seed: int) -> dict:
    """Monte Carlo with Metropolis-Hastings acceptance."""
    model = HP3DLattice(sequence)
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
            current = Conformation3D(new_positions, new_energy, sequence)
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
# FORGETTING ENGINE ALGORITHM (verbatim from validated study)
# ============================================================================

def forgetting_engine_3d(sequence: str, pop_size: int, forget_rate: float,
                         max_gen: int, seed: int) -> dict:
    """Forgetting Engine with paradox retention tracking."""
    model = HP3DLattice(sequence)
    rng = np.random.RandomState(seed)

    population = [model.random_walk(seed + i) for i in range(pop_size)]
    paradox_buffer = []
    paradox_retained_count = 0

    start_time = datetime.now()
    best = min(population, key=lambda x: x.energy)

    for gen in range(max_gen):
        population.sort(key=lambda x: x.energy)

        # Strategic forgetting
        cutoff = int(pop_size * (1 - forget_rate))
        forgotten = population[cutoff:]
        population = population[:cutoff]

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
                    population.append(Conformation3D(child_positions, child_energy, sequence))
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
# SEQUENCE GENERATOR (new for scaling study)
# ============================================================================

def generate_sequence(length: int, seed: int) -> str:
    """
    Generate a random HP sequence of given length with fixed seed.

    Uses ~50% H ratio to ensure meaningful folding landscape.
    One sequence per length, same for all trials at that length.
    """
    rng = np.random.RandomState(seed)
    return ''.join(rng.choice(['H', 'P'], p=[0.5, 0.5]) for _ in range(length))
