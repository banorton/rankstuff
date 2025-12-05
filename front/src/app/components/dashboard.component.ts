import { Component } from '@angular/core';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  template: `
    <h1>Dashboard</h1>

    <section aria-labelledby="summary-heading">
      <h2 id="summary-heading">Democratic Voting Systems and the Borda Count</h2>
      <p>
        Democratic voting systems are fundamental to collective decision-making, yet the method
        used to count votes can dramatically affect outcomes. Traditional plurality voting, where
        voters select a single candidate and the one with the most votes wins, often fails to
        capture voter preferences when multiple candidates compete. This limitation has led to
        the development of ranked-choice voting methods, which allow voters to express preferences
        beyond their top choice.
      </p>
      <p>
        The Borda count, named after 18th-century French mathematician Jean-Charles de Borda,
        assigns points based on ranking position. In a race with N candidates, a first-place
        vote earns N points, second place earns N-1, and so on. This approach rewards candidates
        with broad support rather than just passionate minorities. Other systems like Instant
        Runoff Voting (IRV) eliminate the lowest-ranked candidate iteratively, redistributing
        votes until one candidate achieves a majority.
      </p>
      <p>
        Remarkably, different algorithms applied to identical voter preferences can produce
        different winners, highlighting that "fairness" in voting is not absolute but depends
        on which criteria we prioritize.
      </p>
      <p>
        <strong>Source:</strong>
        <a href="https://en.wikipedia.org/wiki/Comparison_of_electoral_systems" target="_blank" rel="noopener">
          Wikipedia - Comparison of Electoral Systems
        </a>
      </p>
    </section>

    <section aria-labelledby="tech-heading">
      <h2 id="tech-heading">Technical Implementation</h2>
      <p>
        This application is built with a decoupled architecture. The backend uses Python with
        FastAPI, providing RESTful API endpoints secured with JWT authentication. Data is stored
        in MongoDB, a document database hosted on DigitalOcean. The frontend is an Angular
        single-page application that communicates with the backend via HTTP calls. Charts are
        rendered using Chart.js. The application is deployed on a single server with NGINX
        serving the Angular build on port 80 and Uvicorn running the FastAPI backend on port 3000.
      </p>
    </section>
  `,
  styles: [`
    h1 { margin-bottom: 20px; }
    h2 { margin-top: 30px; margin-bottom: 10px; }
    p { line-height: 1.6; margin-bottom: 15px; }
    section { margin-bottom: 30px; }
    a { color: #0066cc; }
  `]
})
export class DashboardComponent {}
