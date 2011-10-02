
(define make-counter
  (lambda (n)
    ((lambda ()
      (cons
        (lambda ()
          (set! n (+ n 1))
          n)
        (lambda ()
          (set! n (- n 1))
          n))))))

(define two (make-counter 0))
(define incr (car two))
(define decr (cdr two))
(display (incr))
(display (incr))
(display (incr))

(display (decr))
(display (decr))
(display (decr))

