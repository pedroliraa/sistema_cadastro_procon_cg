import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { catchError, map, of } from 'rxjs';

import { AuthService } from './auth.service';

// Protege as rotas /admin: sem login → vai para /login.
export const authGuard: CanActivateFn = () => {
  const auth = inject(AuthService);
  const router = inject(Router);

  if (!auth.estaLogado()) {
    return router.createUrlTree(['/login']);
  }

  // Já tem os dados do usuário (navegação normal dentro do site)
  if (auth.usuario()) {
    return true;
  }

  // Recarregou a página: tem token, mas precisa buscar o perfil de novo
  return auth.carregarUsuario().pipe(
    map(() => true),
    catchError(() => {
      auth.limparSessao();
      return of(router.createUrlTree(['/login']));
    })
  );
};
