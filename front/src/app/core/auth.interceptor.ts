import { HttpErrorResponse, HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { catchError, throwError } from 'rxjs';

import { API_URL } from './api';
import { AuthService } from './auth.service';

// Coloca "Authorization: Token <token>" em toda chamada à nossa API.
// Se o back responder 401 (token inválido/expirado), desloga.
export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const auth = inject(AuthService);
  const token = auth.token;

  if (token && req.url.startsWith(API_URL)) {
    req = req.clone({ setHeaders: { Authorization: `Token ${token}` } });
  }

  return next(req).pipe(
    catchError((erro: HttpErrorResponse) => {
      if (erro.status === 401 && token) {
        auth.logout();
      }
      return throwError(() => erro);
    })
  );
};
