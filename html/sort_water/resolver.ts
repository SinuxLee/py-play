// Water Sort Puzzle Solver - TypeScript Implementation
// Compatible with both Chrome and Node.js

enum COLOR {
  RED = 1,
  BLUE,
  GREEN,
  ORANGE,
  PURPLE,
  CYAN,
  YELLOW,
  GRAY,
  MAX
}

const CAPACITY = 4;
const BOTTLE_AMOUNT = 19;
const EMPTY_BOTTLE = 2;

type Bottle = number[];
type State = Bottle[];
type Move = [number, number, number]; // [from, to, count]

interface PriorityQueueItem {
  f: number;
  cost: number;
  state: State;
  path: Move[];
}

class MinHeap {
  private heap: PriorityQueueItem[] = [];

  push(item: PriorityQueueItem): void {
    this.heap.push(item);
    this.bubbleUp(this.heap.length - 1);
  }

  pop(): PriorityQueueItem | undefined {
    if (this.heap.length === 0) return undefined;
    if (this.heap.length === 1) return this.heap.pop();

    const min = this.heap[0];
    this.heap[0] = this.heap.pop()!;
    this.bubbleDown(0);
    return min;
  }

  size(): number {
    return this.heap.length;
  }

  private bubbleUp(index: number): void {
    while (index > 0) {
      const parentIndex = Math.floor((index - 1) / 2);
      if (this.heap[index].f >= this.heap[parentIndex].f) break;
      [this.heap[index], this.heap[parentIndex]] = [this.heap[parentIndex], this.heap[index]];
      index = parentIndex;
    }
  }

  private bubbleDown(index: number): void {
    while (true) {
      const leftChild = 2 * index + 1;
      const rightChild = 2 * index + 2;
      let smallest = index;

      if (leftChild < this.heap.length && this.heap[leftChild].f < this.heap[smallest].f) {
        smallest = leftChild;
      }
      if (rightChild < this.heap.length && this.heap[rightChild].f < this.heap[smallest].f) {
        smallest = rightChild;
      }
      if (smallest === index) break;

      [this.heap[index], this.heap[smallest]] = [this.heap[smallest], this.heap[index]];
      index = smallest;
    }
  }
}

class WaterSortSolver {
  private maxCapacity: number;
  private initialState: State = [];

  constructor(maxCapacity: number = CAPACITY) {
    this.maxCapacity = maxCapacity;
  }

  private countColors(): Map<number, number> {
    const colorCount = new Map<number, number>();
    for (const bottle of this.initialState) {
      for (const color of bottle) {
        colorCount.set(color, (colorCount.get(color) || 0) + 1);
      }
    }
    return colorCount;
  }

  changePuzzle(bottles: State): void {
    this.initialState = bottles.map(b => [...b]);
  }

  genNewPuzzle(): State {
    const colorBlocks: number[] = [];
    for (let i = 0; i < BOTTLE_AMOUNT - EMPTY_BOTTLE; i++) {
      const color = Math.floor(Math.random() * (COLOR.MAX - COLOR.RED)) + COLOR.RED;
      for (let j = 0; j < CAPACITY; j++) {
        colorBlocks.push(color);
      }
    }

    // Shuffle
    for (let i = colorBlocks.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [colorBlocks[i], colorBlocks[j]] = [colorBlocks[j], colorBlocks[i]];
    }

    const bottles: State = Array.from({ length: BOTTLE_AMOUNT }, () => []);
    let blockIndex = 0;
    for (let idx = 0; idx < bottles.length; idx++) {
      const count = idx < 2 ? CAPACITY / 2 : CAPACITY;
      bottles[idx] = colorBlocks.slice(blockIndex, blockIndex + count);
      blockIndex += count;
    }

    return bottles;
  }

  async genSomeValidPuzzle(count: number = 100): Promise<void> {
    for (let i = 0; i < count; i++) {
      const puzzle = this.genNewPuzzle();
      this.changePuzzle(puzzle);
      const solution = this.solve(10000, 3);
      if (!solution) continue;
      
      console.log(JSON.stringify(puzzle));
    }
  }

  private getTopColorCount(bottle: Bottle): [number | null, number] {
    if (bottle.length === 0) return [null, 0];

    const color = bottle[bottle.length - 1];
    let count = 0;
    for (let i = bottle.length - 1; i >= 0; i--) {
      if (bottle[i] === color) {
        count++;
      } else {
        break;
      }
    }
    return [color, count];
  }

  private isBottleComplete(bottle: Bottle): boolean {
    return bottle.length === this.maxCapacity && new Set(bottle).size === 1;
  }

  private isBottleSingleColor(bottle: Bottle): boolean {
    return bottle.length > 0 && new Set(bottle).size === 1;
  }

  private countCompleteBottles(bottles: State): number {
    return bottles.filter(b => this.isBottleComplete(b)).length;
  }

  private isValidPour(fromBottle: Bottle, toBottle: Bottle): boolean {
    if (fromBottle.length === 0 || toBottle.length >= this.maxCapacity) {
      return false;
    }

    if (toBottle.length === 0) {
      return true;
    }

    return fromBottle[fromBottle.length - 1] === toBottle[toBottle.length - 1];
  }

  private isUsefulMove(state: State, fromIdx: number, toIdx: number): boolean {
    const fromBottle = state[fromIdx];
    const toBottle = state[toIdx];

    if (this.isBottleComplete(fromBottle)) return false;
    if (this.isBottleComplete(toBottle)) return false;

    if (toBottle.length === 0 && this.isBottleSingleColor(fromBottle)) {
      if (fromBottle.length === this.maxCapacity) return false;
    }

    if (this.isBottleSingleColor(fromBottle) && this.isBottleSingleColor(toBottle)) {
      if (fromBottle[fromBottle.length - 1] === toBottle[toBottle.length - 1]) {
        const [, fromCount] = this.getTopColorCount(fromBottle);
        const total = toBottle.length + fromCount;
        if (total < this.maxCapacity) return false;
      }
    }

    if (toBottle.length >= 2) {
      const bottomColor = toBottle[0];
      const isBottomSorted = toBottle.every(c => c === bottomColor);
      if (isBottomSorted && fromBottle[fromBottle.length - 1] !== bottomColor) {
        return false;
      }
    }

    return true;
  }

  private pourWater(bottles: State, fromIdx: number, toIdx: number): [State, number] {
    const newBottles: State = bottles.map(b => [...b]);
    const fromBottle = newBottles[fromIdx];
    const toBottle = newBottles[toIdx];

    const color = fromBottle[fromBottle.length - 1];
    let count = 0;

    while (
      fromBottle.length > 0 &&
      fromBottle[fromBottle.length - 1] === color &&
      toBottle.length < this.maxCapacity
    ) {
      toBottle.push(fromBottle.pop()!);
      count++;
    }

    return [newBottles, count];
  }

  private isSolved(bottles: State): boolean {
    for (const bottle of bottles) {
      if (bottle.length === 0) continue;
      if (bottle.length !== this.maxCapacity || new Set(bottle).size !== 1) {
        return false;
      }
    }
    return true;
  }

  private stateToString(bottles: State): string {
    return JSON.stringify(bottles);
  }

  private getHeuristic(bottles: State): number {
    const colorBottles = new Map<number, number[]>();
    for (let i = 0; i < bottles.length; i++) {
      const uniqueColors = new Set(bottles[i]);
      for (const color of uniqueColors) {
        if (!colorBottles.has(color)) {
          colorBottles.set(color, []);
        }
        colorBottles.get(color)!.push(i);
      }
    }

    let h = 0;
    for (const [color, bottleIndices] of colorBottles) {
      h += (bottleIndices.length - 1) * 2;

      for (const idx of bottleIndices) {
        const bottle = bottles[idx];
        if (this.isBottleComplete(bottle)) continue;

        const [topColor] = this.getTopColorCount(bottle);
        if (topColor !== color) {
          let layersAbove = 0;
          for (let i = bottle.length - 1; i >= 0; i--) {
            if (bottle[i] === color) break;
            layersAbove++;
          }
          h += layersAbove;
        }
      }
    }

    const incomplete = bottles.filter(b => b.length > 0 && !this.isBottleComplete(b)).length;
    h += incomplete * 0.5;

    return h;
  }

  private getPriorityMoves(state: State): [number, number][] {
    const moves: [number, number, number][] = [];

    for (let i = 0; i < state.length; i++) {
      if (state[i].length === 0 || this.isBottleComplete(state[i])) continue;

      const [fromColor, fromCount] = this.getTopColorCount(state[i]);

      for (let j = 0; j < state.length; j++) {
        if (i === j) continue;
        if (!this.isValidPour(state[i], state[j])) continue;
        if (!this.isUsefulMove(state, i, j)) continue;

        let priority = 0;
        const [toColor, toCount] = this.getTopColorCount(state[j]);
        const canPour = Math.min(fromCount, this.maxCapacity - state[j].length);

        if (toColor === fromColor) {
          const total = state[j].length + canPour;
          if (total === this.maxCapacity) {
            priority += 1000;
          } else if (total > this.maxCapacity * 0.75) {
            priority += 500;
          }
        }

        if (state[i].length === fromCount) {
          priority += 300;
        }

        if (state[j].length > 0 && toColor === fromColor) {
          priority += 200;
        }

        if (state[j].length === 0) {
          if (this.isBottleSingleColor(state[i]) && state[i].length === this.maxCapacity) {
            priority += 10;
          } else {
            priority += 150;
          }
        }

        priority += canPour * 10;

        if (this.isBottleSingleColor(state[i])) {
          priority += 100;
        }

        moves.push([priority, i, j]);
      }
    }

    moves.sort((a, b) => b[0] - a[0]);
    return moves.slice(0, 15).map(([, i, j]) => [i, j]);
  }

  solve(maxSteps: number = 500000, timeLimit: number = 300): Move[] | null {
    const startTime = Date.now();

    const initialH = this.getHeuristic(this.initialState);
    const heap = new MinHeap();
    heap.push({ f: initialH, cost: 0, state: this.initialState, path: [] });
    
    const visited = new Set<string>();
    visited.add(this.stateToString(this.initialState));

    let steps = 0;
    let bestComplete = 0;

    while (heap.size() > 0) {
      steps++;

      const elapsed = (Date.now() - startTime) / 1000;
      if (elapsed > timeLimit) return null;
      if (steps > maxSteps) return null;

      const item = heap.pop()!;
      const { cost, state: currentState, path } = item;

      if (this.isSolved(currentState)) {
        return path;
      }

      const complete = this.countCompleteBottles(currentState);
      if (complete > bestComplete) {
        bestComplete = complete;
      }

      const priorityMoves = this.getPriorityMoves(currentState);

      for (const [i, j] of priorityMoves) {
        const [newState, count] = this.pourWater(currentState, i, j);
        const stateStr = this.stateToString(newState);

        if (!visited.has(stateStr)) {
          visited.add(stateStr);
          const newCost = cost + 1;
          const h = this.getHeuristic(newState);
          const f = newCost + h;
          const newPath: Move[] = [...path, [i, j, count]];
          heap.push({ f, cost: newCost, state: newState, path: newPath });
        }
      }
    }

    return null;
  }

  printSolution(solution: Move[] | null, verbose: boolean = true): void {
    if (solution === null) {
      console.log("No solution found");
      return;
    }

    console.log("\n" + "=".repeat(70));
    console.log(`Found solution in ${solution.length} steps`);
    console.log("=".repeat(70) + "\n");

    if (!verbose && solution.length > 20) {
      console.log("(Long solution, showing key steps only)\n");
    }

    let state = this.initialState.map(b => [...b]);

    if (verbose) {
      console.log("Initial state:");
      this.printState(state);
      console.log();
    }

    for (let stepNum = 0; stepNum < solution.length; stepNum++) {
      const [fromIdx, toIdx, count] = solution[stepNum];
      [state] = this.pourWater(state, fromIdx, toIdx);

      if (verbose || solution.length <= 20) {
        console.log(`Step ${stepNum + 1}: Bottle ${fromIdx} → Bottle ${toIdx} (${count} units)`);
        if (verbose) {
          this.printState(state);
          console.log();
        }
      } else if ((stepNum + 1) % 10 === 0 || stepNum === solution.length - 1) {
        console.log(`Step ${stepNum + 1}: Bottle ${fromIdx} → Bottle ${toIdx} (${count} units)`);
      }
    }

    if (!verbose) {
      console.log("\nFinal state:");
      this.printState(state);
    }
  }

  printState(bottles: State): void {
    for (let i = 0; i < bottles.length; i++) {
      const status = this.isBottleComplete(bottles[i]) ? " ✓" : "";
      console.log(`Bottle ${i.toString().padStart(2)}: ${JSON.stringify(bottles[i])}${status}`);
    }
  }
}

// Example usage
if (typeof window === 'undefined') {
  // Node.js environment
  const solver = new WaterSortSolver();
  solver.genSomeValidPuzzle(100);
} else {
  // Browser environment - export for use
  (window as any).WaterSortSolver = WaterSortSolver;
  (window as any).COLOR = COLOR;
}

export { WaterSortSolver, COLOR };