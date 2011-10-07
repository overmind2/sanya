(define display/cc
  (lambda (thing k)
    (k (display thing))))

((lambda (cont)
  (cont ((lambda (cont)
           (cont display/cc))
         (lambda (cps-t-0)
           ((lambda (cont)
              (cont 1))
            (lambda (cps-t-1)
              (cps-t-0 cps-t-1 cont)))))))
 (lambda (_) _))

