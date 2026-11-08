import { Routes } from '@angular/router';
import { ConsultaPublica } from './pages/consulta-publica/consulta-publica';

export const routes: Routes = [
  {
    path: 'consulta-publica',
    component: ConsultaPublica,
  },
  {
    path: '',
    redirectTo: 'consulta-publica',
    pathMatch: 'full',
  },
];