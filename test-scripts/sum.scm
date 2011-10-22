(define sum1
  (lambda (n accu)
    (if (< 0 n)
      (sum1 (- n 4) (+ accu n (- n 1) (- n 2) (- n 3)))
      accu)))

(define sum
  (lambda (n)
    (sum1 n 0)))

(display (sum 10000000))

