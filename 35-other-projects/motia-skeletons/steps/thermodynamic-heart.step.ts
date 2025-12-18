/**
 * Thermodynamic Love Engine
 * Enforces Love ⟂ Sycophancy via vector projections
 */

import { PanopticonEntry } from '../types/shared-types';

export class ThermodynamicHeart {
  private sycophancyTolerance: number = 0.3;
  private loveVector: number[] = [];
  private sycophancyVector: number[] = [];

  /**
   * Apply thermodynamic steering to response
   */
  applyThermodynamicSteering(intentVector: number[], responseVector: number[]): number[] {
    try {
      // Compute sycophancy projection
      const sycophancyProjection = this.projectVector(responseVector, this.sycophancyVector);
      const sycophancyMagnitude = this.vectorMagnitude(sycophancyProjection);

      // Check if correction is needed
      if (sycophancyMagnitude > this.sycophancyTolerance) {
        // Project response back into safe set
        const correctedResponse = this.correctSycophancy(responseVector, sycophancyProjection);
        
        // Log correction
        this.logCorrection(sycophancyMagnitude, 'Sycophancy correction applied');
        
        return correctedResponse;
      }

      return responseVector;
    } catch (error) {
      console.error('[HEART] Steering error:', error);
      // Return safe fallback
      return this.generateClarifyingQuestion();
    }
  }

  /**
   * Get named vector (love, sycophancy, etc.)
   */
  getVector(name: string): number[] {
    switch (name.toLowerCase()) {
      case 'love':
        return this.loveVector.length > 0 ? this.loveVector : this.initializeLoveVector();
      case 'sycophancy':
        return this.sycophancyVector.length > 0 ? this.sycophancyVector : this.initializeSycophancyVector();
      default:
        throw new Error(`Unknown vector: ${name}`);
    }
  }

  /**
   * Calculate KL divergence between two probability distributions
   */
  calculateKLDivergence(p: number[], q: number[]): number {
    if (p.length !== q.length) {
      throw new Error('Vectors must have same length for KL divergence');
    }

    let divergence = 0;
    for (let i = 0; i < p.length; i++) {
      if (p[i] > 0 && q[i] > 0) {
        divergence += p[i] * Math.log(p[i] / q[i]);
      }
    }
    return divergence;
  }

  /**
   * Project vector a onto vector b
   */
  private projectVector(a: number[], b: number[]): number[] {
    if (a.length !== b.length) {
      throw new Error('Vectors must have same length for projection');
    }

    const dotProduct = this.dotProduct(a, b);
    const bMagnitudeSquared = this.dotProduct(b, b);
    
    if (bMagnitudeSquared === 0) {
      return new Array(a.length).fill(0);
    }

    const scalar = dotProduct / bMagnitudeSquared;
    return b.map(component => component * scalar);
  }

  /**
   * Calculate dot product of two vectors
   */
  private dotProduct(a: number[], b: number[]): number {
    return a.reduce((sum, val, i) => sum + val * b[i], 0);
  }

  /**
   * Calculate vector magnitude
   */
  private vectorMagnitude(vector: number[]): number {
    return Math.sqrt(vector.reduce((sum, val) => sum + val * val, 0));
  }

  /**
   * Correct sycophancy in response vector
   */
  private correctSycophancy(responseVector: number[], sycophancyProjection: number[]): number[] {
    // Remove sycophancy component and project toward love
    const corrected = responseVector.map((val, i) => val - sycophancyProjection[i]);
    
    // Add love component
    const loveProjection = this.projectVector(corrected, this.loveVector);
    return corrected.map((val, i) => val + loveProjection[i] * 0.1); // Small love boost
  }

  /**
   * Generate clarifying question as fallback
   */
  private generateClarifyingQuestion(): number[] {
    // TODO: Implement proper clarifying question vector
    // Placeholder: return neutral vector
    return new Array(this.loveVector.length || 100).fill(0);
  }

  /**
   * Initialize love vector
   */
  private initializeLoveVector(): number[] {
    // TODO: Load from trained model or configuration
    // Placeholder: positive values representing care, empathy, helpfulness
    this.loveVector = new Array(100).fill(0).map(() => Math.random() * 0.5 + 0.5);
    return this.loveVector;
  }

  /**
   * Initialize sycophancy vector
   */
  private initializeSycophancyVector(): number[] {
    // TODO: Load from trained model or configuration
    // Placeholder: values representing flattery, false agreement
    this.sycophancyVector = new Array(100).fill(0).map(() => Math.random() * 0.3);
    return this.sycophancyVector;
  }

  /**
   * Log correction to panopticon
   */
  private logCorrection(magnitude: number, reason: string): void {
    const entry: PanopticonEntry = {
      timestamp: new Date().toISOString(),
      type: 'love_correction',
      data: { magnitude, reason },
      severity: magnitude > 0.7 ? 'high' : 'medium'
    };

    // TODO: Implement actual panopticon logging
    console.log('[HEART] Correction logged:', entry);
  }
}