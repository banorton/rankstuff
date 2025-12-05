import { Routes } from '@angular/router';
import { authGuard } from './guards/auth.guard';
import { LoginComponent } from './components/login.component';
import { LayoutComponent } from './components/layout.component';
import { DashboardComponent } from './components/dashboard.component';
import { SummaryComponent } from './components/summary.component';
import { ReportsComponent } from './components/reports.component';
import { PollsComponent } from './components/polls.component';
import { HistoryComponent } from './components/history.component';

export const routes: Routes = [
  { path: 'login', component: LoginComponent },
  {
    path: '',
    component: LayoutComponent,
    canActivate: [authGuard],
    children: [
      { path: '', redirectTo: 'create', pathMatch: 'full' },
      { path: 'create', component: PollsComponent },
      { path: 'poll/:id', component: PollsComponent },
      { path: 'history', component: HistoryComponent },
      { path: 'dashboard', component: DashboardComponent },
      { path: 'summary', component: SummaryComponent },
      { path: 'reports', component: ReportsComponent }
    ]
  },
  { path: '**', redirectTo: '' }
];
