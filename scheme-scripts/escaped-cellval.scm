
(define make-counter
  (lambda (n)
    (lambda ()
      (define res n)
      (set! n (+ n 1))
      res)))

(define a (make-counter 9))
(display (a))
(display (a))
(display (a))

