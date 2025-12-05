import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { AuthService } from './auth.service';
import { environment } from '../../environments/environment';

export interface AlgorithmScore {
  algorithm: string;
  winner: string;
  scores: { [key: string]: number };
}

export interface AlgorithmComparisonChart {
  title: string;
  description: string;
  source_url: string;
  data: AlgorithmScore[];
}

export interface OptionDistribution {
  option: string;
  first: number;
  second: number;
  third: number;
}

export interface VoteDistributionChart {
  title: string;
  description: string;
  source_url: string;
  data: OptionDistribution[];
}

@Injectable({ providedIn: 'root' })
export class ChartService {
  private apiUrl = environment.apiUrl;

  constructor(private http: HttpClient, private auth: AuthService) {}

  private getHeaders(): HttpHeaders {
    const token = this.auth.getToken();
    return new HttpHeaders({
      'Authorization': `Bearer ${token}`
    });
  }

  getAlgorithmComparison(): Observable<AlgorithmComparisonChart> {
    return this.http.get<AlgorithmComparisonChart>(
      `${this.apiUrl}/charts/algorithm-comparison`,
      { headers: this.getHeaders() }
    );
  }

  getVoteDistribution(): Observable<VoteDistributionChart> {
    return this.http.get<VoteDistributionChart>(
      `${this.apiUrl}/charts/vote-distribution`,
      { headers: this.getHeaders() }
    );
  }
}
