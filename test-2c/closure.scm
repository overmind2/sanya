(define (print x)
  (display x)
  (newline))

(define (fibo n)
  (if (< n 2) n
    (+ (fibo (- n 1))
       (fibo (- n 2)))))

;; TCO
(define (sum n)
  (define (sum1 n accu)
    (if (< n 1) accu
      (sum1 (- n 1) (+ n accu))))
  (sum1 n 0))

(define (main)
  (print (cons 3 (cons 2 (cons 1 '()))))
  (print (fibo 4)))

(main)

