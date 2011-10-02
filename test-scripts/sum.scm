((lambda ()
 (define lt <)
 (define minus -)
 (define add +)

 (define sum1
   (lambda (n accu)
     (if (lt 0 n)
       (sum1 (minus n 4) (add accu n (minus n 1) (minus n 2) (minus n 3)))
       accu)))

 (define sum
   (lambda (n)
     (sum1 n 0)))

 (display (sum 10000000))))

